"""Pydantic models for function definitions and function-call results."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class ParamType(str, Enum):
    """Valid parameter types"""
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"


class ParamSpec(BaseModel):
    """Force the entry of parameters to be of name 'type'. Specification of a
      single parameter or return value"""
    model_config = ConfigDict(extra="forbid")
    type: ParamType


class FunctionDefinition(BaseModel):
    """Same as before, but with its own parameters. A callable function: name,
      description, typed parameters and return type."""
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    parameters: dict[str, ParamSpec]
    returns: ParamSpec


class FunctionCallResult(BaseModel):
    """Structured function call produced for a single
    prompt (output schema)."""
    prompt: str
    name: str
    parameters: dict[str, Any]
