from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AVEContractError(Exception):
    """Raised when an AVE payload does not match the documented contract."""


def _parse_bool_like(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in {"1", "true", "yes"}:
            return True
        if cleaned in {"0", "false", "no"}:
            return False
    return None


def _parse_int_like(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(round(value))
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "").replace(",", "")
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        try:
            return int(round(float(cleaned)))
        except ValueError:
            return None
    return None


def _parse_float_like(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "").replace(",", "")
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


class AVEEnvelope(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: int | None = None
    msg: str | None = None
    data_type: int | None = None
    data: Any = None


class AVETopicPayload(BaseModel):
    """
    Contract for `GET /v2/ranks/topics`.

    The official current docs show this endpoint returning topic identifiers and
    localized display names only. AVERT must derive topic momentum from the
    ranked token lists behind each topic rather than assuming extra topic-level
    analytics are present upstream.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    name_en: str | None = None
    name_zh: str | None = None


class AVERankedTokenPayload(BaseModel):
    """
    Contract for `GET /v2/ranks?topic={topic}`.

    These fields are the current documented live fields AVERT relies on to
    compute flow, acceleration, breadth, capital demand, and candidate quality.
    """

    model_config = ConfigDict(extra="allow")

    token: str
    chain: str
    decimal: int | None = None
    name: str | None = None
    symbol: str | None = None
    holders: int | None = None
    risk_level: int | None = None
    risk_score: int | None = None
    total: float | None = None
    launch_price: float | None = None
    current_price_eth: float | None = None
    current_price_usd: float | None = None
    price_change_1d: float | None = None
    price_change_24h: float | None = None
    tx_amount_24h: float | None = None
    tx_volume_u_24h: float | None = None
    market_cap: float | None = None
    fdv: float | None = None
    tvl: float | None = None
    main_pair_tvl: float | None = None
    token_price_change_5m: float | None = None
    token_price_change_1h: float | None = None
    token_price_change_4h: float | None = None
    token_price_change_24h: float | None = None
    token_tx_volume_usd_5m: float | None = None
    token_tx_volume_usd_1h: float | None = None
    token_tx_volume_usd_4h: float | None = None
    token_tx_volume_usd_24h: float | None = None
    token_buy_volume_u_5m: float | None = None
    token_sell_volume_u_5m: float | None = None
    token_buy_tx_volume_usd_5m: float | None = None
    token_sell_tx_volume_usd_5m: float | None = None
    token_buy_tx_count_5m: int | None = None
    token_sell_tx_count_5m: int | None = None
    token_buyers_5m: int | None = None
    token_sellers_5m: int | None = None
    buy_tx: int | None = None
    sell_tx: int | None = None
    tx_count_24h: int | None = None
    token_tx_count_1h: int | None = None
    token_tx_count_4h: int | None = None
    token_tx_count_24h: int | None = None
    token_buy_tx_count_1h: int | None = None
    token_buy_tx_count_4h: int | None = None
    token_buy_tx_count_24h: int | None = None
    token_sell_tx_count_1h: int | None = None
    token_sell_tx_count_4h: int | None = None
    token_sell_tx_count_24h: int | None = None
    token_makers_1h: int | None = None
    token_makers_4h: int | None = None
    token_makers_24h: int | None = None
    token_buyers_1h: int | None = None
    token_buyers_4h: int | None = None
    token_buyers_24h: int | None = None
    token_sellers_1h: int | None = None
    token_sellers_4h: int | None = None
    token_sellers_24h: int | None = None
    appendix: str | None = None
    intro_en: str | None = None
    logo_url: str | None = None
    main_pair: str | None = None
    created_at: int | None = None
    updated_at: int | None = None

    @property
    def token_id(self) -> str:
        return f"{self.token}-{self.chain}"

    @field_validator(
        "decimal",
        "holders",
        "risk_level",
        "risk_score",
        "tx_count_24h",
        "token_tx_count_1h",
        "token_tx_count_4h",
        "token_tx_count_24h",
        "token_buy_tx_count_1h",
        "token_buy_tx_count_4h",
        "token_buy_tx_count_24h",
        "token_buy_tx_count_5m",
        "token_sell_tx_count_1h",
        "token_sell_tx_count_4h",
        "token_sell_tx_count_24h",
        "token_sell_tx_count_5m",
        "token_makers_1h",
        "token_makers_4h",
        "token_makers_24h",
        "token_buyers_1h",
        "token_buyers_4h",
        "token_buyers_24h",
        "token_buyers_5m",
        "token_sellers_1h",
        "token_sellers_4h",
        "token_sellers_24h",
        "token_sellers_5m",
        "buy_tx",
        "sell_tx",
        "created_at",
        "updated_at",
        mode="before",
    )
    @classmethod
    def _coerce_ints(cls, value: Any) -> int | None:
        return _parse_int_like(value)

    @field_validator(
        "total",
        "launch_price",
        "current_price_eth",
        "current_price_usd",
        "price_change_1d",
        "price_change_24h",
        "tx_amount_24h",
        "tx_volume_u_24h",
        "market_cap",
        "fdv",
        "tvl",
        "main_pair_tvl",
        "token_price_change_5m",
        "token_price_change_1h",
        "token_price_change_4h",
        "token_price_change_24h",
        "token_tx_volume_usd_5m",
        "token_tx_volume_usd_1h",
        "token_tx_volume_usd_4h",
        "token_tx_volume_usd_24h",
        "token_buy_volume_u_5m",
        "token_sell_volume_u_5m",
        "token_buy_tx_volume_usd_5m",
        "token_sell_tx_volume_usd_5m",
        mode="before",
    )
    @classmethod
    def _coerce_floats(cls, value: Any) -> float | None:
        return _parse_float_like(value)


class AVERiskDexPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    amm: str | None = None
    liquidity: float | None = None
    name: str | None = None
    pair: str | None = None

    @field_validator("liquidity", mode="before")
    @classmethod
    def _coerce_liquidity(cls, value: Any) -> float | None:
        return _parse_float_like(value)


class AVESmartWalletTagItemPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    address: str | None = None
    symbol: str | None = None
    volume: float | None = None

    @field_validator("volume", mode="before")
    @classmethod
    def _coerce_volume(cls, value: Any) -> float | None:
        return _parse_float_like(value)


class AVESmartWalletPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    wallet_address: str
    chain: str | None = None
    tag: str | None = None
    extra_info: str | None = None
    total_trades: int | None = None
    total_volume: float | None = None
    total_profit_rate: float | None = None
    tag_items: list[AVESmartWalletTagItemPayload] = Field(default_factory=list)

    @field_validator("total_trades", mode="before")
    @classmethod
    def _coerce_total_trades(cls, value: Any) -> int | None:
        return _parse_int_like(value)

    @field_validator("total_volume", "total_profit_rate", mode="before")
    @classmethod
    def _coerce_smart_wallet_floats(cls, value: Any) -> float | None:
        return _parse_float_like(value)

    @field_validator("tag_items", mode="before")
    @classmethod
    def _coerce_tag_items(cls, value: Any) -> list[dict[str, Any]] | list[Any]:
        return value if isinstance(value, list) else []


class AVEPublicSignalActionPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    wallet_address: str | None = None
    action_type: str | None = None
    action_time: int | None = None

    @field_validator("id", "action_time", mode="before")
    @classmethod
    def _coerce_signal_action_ints(cls, value: Any) -> int | None:
        return _parse_int_like(value)


class AVEPublicSignalPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    token: str | None = None
    chain: str | None = None
    symbol: str | None = None
    signal_type: str | None = None
    tag: str | None = None
    action_count: int | None = None
    history_count: int | None = None
    actions: list[AVEPublicSignalActionPayload] = Field(default_factory=list)

    @field_validator("id", "action_count", "history_count", mode="before")
    @classmethod
    def _coerce_signal_ints(cls, value: Any) -> int | None:
        return _parse_int_like(value)

    @field_validator("actions", mode="before")
    @classmethod
    def _coerce_signal_actions(cls, value: Any) -> list[dict[str, Any]] | list[Any]:
        return value if isinstance(value, list) else []


class AVETrendingTokensPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_page_size: int | None = None
    next_page: int | None = None
    total: int | None = None
    tokens: list[AVERankedTokenPayload] = Field(default_factory=list)

    @field_validator("current_page_size", "next_page", "total", mode="before")
    @classmethod
    def _coerce_trending_ints(cls, value: Any) -> int | None:
        return _parse_int_like(value)

    @field_validator("tokens", mode="before")
    @classmethod
    def _coerce_trending_tokens(cls, value: Any) -> list[dict[str, Any]] | list[Any]:
        return value if isinstance(value, list) else []


class AVESupportedChainPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    chain: str | None = None
    id: str | None = None
    name: str | None = None
    symbol: str | None = None


class AVEKlinePointPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    amount: float | None = None
    time: int | None = None

    @field_validator("open", "high", "low", "close", "volume", "amount", mode="before")
    @classmethod
    def _coerce_floats(cls, value: Any) -> float | None:
        return _parse_float_like(value)

    @field_validator("time", mode="before")
    @classmethod
    def _coerce_time(cls, value: Any) -> int | None:
        return _parse_int_like(value)


class AVEKlinePayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    points: list[AVEKlinePointPayload] = Field(default_factory=list)

    @field_validator("points", mode="before")
    @classmethod
    def _coerce_points(cls, value: Any) -> list[dict[str, Any]] | list[Any]:
        return value if isinstance(value, list) else []


class AVEHolderPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    holder: str | None = None
    address: str | None = None
    balance_ratio: float | None = None

    @field_validator("balance_ratio", mode="before")
    @classmethod
    def _coerce_balance_ratio(cls, value: Any) -> float | None:
        return _parse_float_like(value)


class AVETokenDetailPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    token: AVERankedTokenPayload | None = None
    pairs: list[dict[str, Any]] = Field(default_factory=list)
    is_audited: bool | None = None

    @field_validator("pairs", mode="before")
    @classmethod
    def _coerce_pairs(cls, value: Any) -> list[dict[str, Any]] | list[Any]:
        return value if isinstance(value, list) else []

    @field_validator("is_audited", mode="before")
    @classmethod
    def _coerce_is_audited(cls, value: Any) -> bool | None:
        return _parse_bool_like(value)


class AVERiskTaxDistributionPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    count: int | None = None
    tax: float | None = None

    @field_validator("count", mode="before")
    @classmethod
    def _coerce_count(cls, value: Any) -> int | None:
        return _parse_int_like(value)

    @field_validator("tax", mode="before")
    @classmethod
    def _coerce_tax(cls, value: Any) -> float | None:
        return _parse_float_like(value)


class AVERiskHolderAnalysisPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    average_tax: float | None = None
    balance_disappeared: int | None = None
    sell_failure: int | None = None
    sell_successful: int | None = None
    simulate_holders: int | None = None
    tax_distribution: list[AVERiskTaxDistributionPayload] = Field(default_factory=list)

    @field_validator(
        "average_tax",
        mode="before",
    )
    @classmethod
    def _coerce_average_tax(cls, value: Any) -> float | None:
        return _parse_float_like(value)

    @field_validator(
        "balance_disappeared",
        "sell_failure",
        "sell_successful",
        "simulate_holders",
        mode="before",
    )
    @classmethod
    def _coerce_holder_counts(cls, value: Any) -> int | None:
        return _parse_int_like(value)

    @field_validator("tax_distribution", mode="before")
    @classmethod
    def _coerce_tax_distribution(cls, value: Any) -> list[dict[str, Any]] | list[Any]:
        return value if isinstance(value, list) else []


class AVEContractRiskPayload(BaseModel):
    """
    Contract for `GET /v2/contracts/{token-id}`.

    The official current docs expose a risk report rather than the compact
    execution-oriented summary AVERT previously assumed. AVERT now derives route
    quality and execution readiness from the documented DEX liquidity, LP
    adequacy, tax, and risk flags in this payload.
    """

    model_config = ConfigDict(extra="allow")

    token: str
    chain: str
    risk_score: int | None = None
    holders: int | None = None
    analysis_lp_current_adequate: bool | None = None
    analysis_lp_current_volume: float | None = None
    analysis_big_wallet: bool | None = None
    analysis_creator_gt_5percent: int | None = None
    analysis_lp_creator_gt_5percent: int | None = None
    analysis_scam_wallet: bool | None = None
    anti_whale_modifiable: bool | None = None
    buy_tax: float | None = None
    sell_tax: float | None = None
    can_take_back_ownership: bool | None = None
    cannot_buy: bool | None = None
    cannot_sell_all: bool | None = None
    external_call: bool | None = None
    has_black_method: bool | None = None
    has_code: bool | None = None
    has_mint_method: bool | None = None
    has_owner_removed_risk: bool | None = None
    has_white_method: bool | None = None
    hidden_owner: bool | None = None
    holder_analysis: AVERiskHolderAnalysisPayload | None = None
    honeypot_with_same_creator: bool | None = None
    is_anti_whale: bool | None = None
    is_honeypot: int | None = None
    is_in_dex: bool | None = None
    is_proxy: bool | None = None
    lock_amount: float | None = None
    owner: str | None = None
    pair_lock_percent: float | None = None
    pair_total: float | None = None
    personal_slippage_modifiable: bool | None = None
    previous_owner: str | None = None
    query_count: int | None = None
    selfdestruct: bool | None = None
    slippage_modifiable: bool | None = None
    buy_gas: float | None = None
    sell_gas: float | None = None
    approve_gas: float | None = None
    creator_address: str | None = None
    creator_percent: float | None = None
    owner_percent: float | None = None
    dex: list[AVERiskDexPayload] = Field(default_factory=list)
    err_code: str | None = None
    err_msg: str | None = None

    @field_validator(
        "risk_score",
        "holders",
        "analysis_creator_gt_5percent",
        "analysis_lp_creator_gt_5percent",
        "query_count",
        "is_honeypot",
        mode="before",
    )
    @classmethod
    def _coerce_ints(cls, value: Any) -> int | None:
        return _parse_int_like(value)

    @field_validator(
        "analysis_lp_current_volume",
        "buy_tax",
        "sell_tax",
        "lock_amount",
        "pair_lock_percent",
        "pair_total",
        "buy_gas",
        "sell_gas",
        "approve_gas",
        "creator_percent",
        "owner_percent",
        mode="before",
    )
    @classmethod
    def _coerce_floats(cls, value: Any) -> float | None:
        return _parse_float_like(value)

    @field_validator(
        "analysis_lp_current_adequate",
        "analysis_big_wallet",
        "analysis_scam_wallet",
        "anti_whale_modifiable",
        "can_take_back_ownership",
        "cannot_buy",
        "cannot_sell_all",
        "external_call",
        "has_black_method",
        "has_code",
        "has_mint_method",
        "has_owner_removed_risk",
        "has_white_method",
        "hidden_owner",
        "honeypot_with_same_creator",
        "is_anti_whale",
        "is_in_dex",
        "is_proxy",
        "personal_slippage_modifiable",
        "selfdestruct",
        "slippage_modifiable",
        mode="before",
    )
    @classmethod
    def _coerce_bools(cls, value: Any) -> bool | None:
        return _parse_bool_like(value)

    @field_validator("holder_analysis", mode="before")
    @classmethod
    def _coerce_holder_analysis(cls, value: Any) -> dict[str, Any] | None:
        return value if isinstance(value, dict) else None

    @field_validator("dex", mode="before")
    @classmethod
    def _coerce_dex(cls, value: Any) -> list[dict[str, Any]] | list[Any]:
        return value if isinstance(value, list) else []


class NormalizedAVENarrativeInput(BaseModel):
    """
    Internal AVE-backed narrative shape consumed by the shared snapshot builder.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    thesis: str
    aveTopicRank: int
    aveRankDelta: int
    flowScore: int
    accelerationScore: int
    breadthScore: int
    breadthTokens: int
    priceExpansionScore: int
    persistenceScore: int
    capitalDemandScore: int
    crowdingScore: int
    leaderConcentration: int
    deteriorationBase: int
    stageBiasHint: str
    competingNarratives: list[str]
    notes: list[str]
    tokenIds: list[str]
    budget: dict[str, str]
    smartMoneySignal: str = "unavailable"


class NormalizedAVETokenInput(BaseModel):
    """
    Internal AVE-backed token shape consumed by the shared snapshot builder.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    narrativeId: str
    symbol: str
    name: str
    leadership: int
    liquidity: int
    routeStability: int
    riskCoverage: int
    smartFlowAlignment: int
    toxicity: int
    scoutSizePct: float
    overlapNarratives: list[str]
    priceExpansionPct: float
    breadthContribution: str
    thesisBreak: str
    hardStopPct: float | None
    timeStopHours: int | None
    routeProvider: str
    signalConfirmations: int = 0
    trendingOnAVE: bool = False
    topHolderPct: float | None = None
    logoUrl: str | None = None
    klineTrend: str = "flat"
    note: str
