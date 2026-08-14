"""Frequency modeling: Poisson and Negative Binomial GLMs."""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.families import NegativeBinomial, Poisson

logger = logging.getLogger("actuarial_platform")


@dataclass
class GLMModelResult:
    """Result container for a fitted GLM."""

    name: str
    coefficients: pd.DataFrame
    aic: float
    bic: float
    deviance: float
    pseudo_r2: float
    diagnostics: dict[str, Any] = field(default_factory=dict)
    model: Any = None


@dataclass
class FrequencyModelResult:
    """Comparison of Poisson vs Negative Binomial frequency models."""

    poisson: GLMModelResult
    negative_binomial: GLMModelResult
    preferred_model: str
    comparison: pd.DataFrame


def _extract_glm_result(name: str, result, model) -> GLMModelResult:
    """Extract standardized metrics from a fitted statsmodels GLM."""
    coef_table = pd.DataFrame(
        {
            "Coefficient": result.params,
            "Std Error": result.bse,
            "z-value": result.tvalues,
            "P-value": result.pvalues,
            "Significant": result.pvalues < 0.05,
        }
    )
    pseudo_r2 = 1 - result.deviance / result.null_deviance if result.null_deviance else 0

    return GLMModelResult(
        name=name,
        coefficients=coef_table.round(6),
        aic=round(result.aic, 2),
        bic=round(result.bic_llf, 2),
        deviance=round(result.deviance, 4),
        pseudo_r2=round(pseudo_r2, 4),
        diagnostics={
            "df_model": result.df_model,
            "df_resid": result.df_resid,
            "pearson_chi2": round(result.pearson_chi2, 4),
            "converged": result.converged,
        },
        model=result,
    )


def _prepare_frequency_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare modeling dataframe with offset and factor variables."""
    data = df.copy()
    data = data[data["Exposure"] > 0].copy()
    data["log_exposure"] = np.log(data["Exposure"])
    for col in ["ProductLine"]:
        data[col] = data[col].astype("category")
    return data


def fit_poisson_glm(df: pd.DataFrame) -> GLMModelResult:
    """
    Fit Poisson GLM for claim frequency.

    Target: ClaimCount
    Features: Exposure (offset), Age, VehicleAge, ProductLine
    """
    data = _prepare_frequency_data(df)
    formula = "ClaimCount ~ Age + VehicleAge + C(ProductLine)"
    model = smf.glm(
        formula,
        data=data,
        family=Poisson(),
        offset=data["log_exposure"],
    )
    result = model.fit()
    logger.info("Poisson GLM fitted: AIC=%.2f", result.aic)
    return _extract_glm_result("Poisson", result, model)


def fit_negative_binomial_glm(df: pd.DataFrame) -> GLMModelResult:
    """
    Fit Negative Binomial GLM for claim frequency.

    Handles overdispersion relative to Poisson.
    """
    data = _prepare_frequency_data(df)
    formula = "ClaimCount ~ Age + VehicleAge + C(ProductLine)"
    model = smf.glm(
        formula,
        data=data,
        family=NegativeBinomial(),
        offset=data["log_exposure"],
    )
    result = model.fit()
    logger.info("Negative Binomial GLM fitted: AIC=%.2f", result.aic)
    return _extract_glm_result("Negative Binomial", result, model)


def fit_frequency_models(df: pd.DataFrame) -> FrequencyModelResult:
    """Fit and compare Poisson and Negative Binomial frequency models."""
    poisson = fit_poisson_glm(df)
    try:
        neg_bin = fit_negative_binomial_glm(df)
    except Exception as exc:
        logger.warning("Negative Binomial fit failed, using Poisson fallback: %s", exc)
        neg_bin = poisson

    comparison = pd.DataFrame(
        [
            {
                "Model": "Poisson",
                "AIC": poisson.aic,
                "BIC": poisson.bic,
                "Deviance": poisson.deviance,
                "Pseudo R²": poisson.pseudo_r2,
            },
            {
                "Model": "Negative Binomial",
                "AIC": neg_bin.aic,
                "BIC": neg_bin.bic,
                "Deviance": neg_bin.deviance,
                "Pseudo R²": neg_bin.pseudo_r2,
            },
        ]
    )

    preferred = (
        "Negative Binomial"
        if neg_bin.aic < poisson.aic
        else "Poisson"
    )

    return FrequencyModelResult(
        poisson=poisson,
        negative_binomial=neg_bin,
        preferred_model=preferred,
        comparison=comparison,
    )


def predict_frequency(
    model_result: GLMModelResult, df: pd.DataFrame
) -> np.ndarray:
    """Predict expected claim frequency per unit exposure."""
    data = _prepare_frequency_data(df)
    predictions = model_result.model.predict(offset=data["log_exposure"])
    return predictions / data["Exposure"].values
