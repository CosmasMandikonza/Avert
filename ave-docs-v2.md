# v2

## Get Your API Key

Please visit <https://cloud.ave.ai/register> to sign up for a new account and get your free API Key. To upgrade your API Key plan, join the <https://t.me/ave_ai_cloud> telegram group to follow the instructions.&#x20;

All API request need the following header present

| Name                                        | Type   | Description                           |
| ------------------------------------------- | ------ | ------------------------------------- |
| X-API-KEY<mark style="color:red;">\*</mark> | string | Your API key needed to access the url |

## Search Token

#### Search for the tokens associated with the given keyword

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/tokens?keyword={keyword}`

The keyword must not be null or empty, search by SYMBOL or CONTRACT ADDRESS, and will return max **300** tokens.

NOTE:

The following fields are not in use. Please use the Contract Risk Detection Report API instead.

```
has_mint_method, is_lp_not_locked, has_not_renounced, 
has_not_audited, has_not_open_source, is_in_blacklist, 
is_honeypot, ave_risk_level
```

#### Query Parameters

<table><thead><tr><th width="135.78515625">Name</th><th width="117.91796875">Type</th><th>Description</th></tr></thead><tbody><tr><td>keyword<mark style="color:red;">*</mark></td><td>string</td><td>The keyword needed to query<br></td></tr><tr><td>chain</td><td>string</td><td>Chain name</td></tr><tr><td>limit</td><td>int</td><td>Default: 100, Max 300</td></tr><tr><td>orderby</td><td>string</td><td>tx_volume_u_24h, main_pair_tvl, fdv, market_cap</td></tr></tbody></table>

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": [
    {
      "total": "999999418.723847",
      "launch_price": "1.2555332002309751",
      "current_price_eth": "0.07299146967305112",
      "current_price_usd": "12.80290508389682",
      "price_change_1d": "0.5",
      "price_change_24h": "-2.01",
      "lock_amount": "800000024.164006",
      "burn_amount": "0",
      "other_amount": "0",
      "tx_amount_24h": "3469410.9516249993",
      "tx_volume_u_24h": "44382214.271629",
      "locked_percent": "0.8000004998222048",
      "market_cap": "2560573265.38647434360095960562",
      "fdv": "12802897641.87340560831422146654",
      "tvl": "391936763.797678",
      "main_pair_tvl": "391936763.797678",
      "token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
      "chain": "solana",
      "decimal": 6,
      "name": "OFFICIAL TRUMP",
      "symbol": "TRUMP",
      "holders": 637672,
      "appendix": "{\"contractAddress\":\"\",\"tokenName\":\"OFFICIAL TRUMP\",\"symbol\":\"TRUMP\",\"divisor\":\"\",\"tokenType\":\"\",\"totalSupply\":\"999999810.732535\",\"blueCheckmark\":\"\",\"description\":\"\",\"website\":\"https://gettrumpmemes.com/\",\"email\":\"\",\"blog\":\"\",\"reddit\":\"\",\"slack\":\"\",\"facebook\":\"\",\"twitter\":\"https://x.com/realDonaldTrump/status/1880446012168249386\",\"btok\":\"\",\"bitcointalk\":\"\",\"github\":\"\",\"telegram\":\"\",\"wechat\":\"\",\"linkedin\":\"\",\"discord\":\"\",\"qq\":\"\",\"whitepaper\":\"\",\"tokenPriceUSD\":\"\"}",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon/solana/6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN_1737366143.png",
      "risk_info": "{\"zh-cn\":\"\",\"zh-tw\":\"\",\"en\":\"\"}",
      "risk_score": "55",
      "launch_at": 1737165695,
      "created_at": 1737165695,
      "tx_count_24h": 6008,
      "lock_platform": "Lock",
      "is_mintable": "0",
      "updated_at": 1748332505,
      "main_pair": "9d9mb8kooFfaD3SctgZtkxQypkshx6ezhbKio89ixyy2",
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    },
    {
      "total": "1000000000",
      "launch_price": "0.000005266564661981724",
      "current_price_eth": "0.000000028450483819641793",
      "current_price_usd": "0.00000496799574392643",
      "price_change_1d": "-5.67",
      "price_change_24h": "-5.67",
      "lock_amount": "0",
      "burn_amount": "0",
      "other_amount": "0",
      "tx_amount_24h": "7815114282.539082",
      "tx_volume_u_24h": "129067.88757302014",
      "locked_percent": "0",
      "market_cap": "4967.99574392643000000000",
      "fdv": "4967.99574392643000000000",
      "tvl": "50.734599",
      "main_pair_tvl": "50.734599",
      "token": "2FtYSbsKA7iGVLiL9AjdyoVsaEdiyYKfvdqcAaiGpump",
      "chain": "solana",
      "decimal": 6,
      "name": "The Cryptologigics",
      "symbol": "TRUMP",
      "holders": 21,
      "appendix": "{\"twitter\": \"https://x.com/Number10cat/status/1927045930504581266\"}",
      "logo_url": "https://www.iconaves.com/ipfs/pump/2FtYSbsKA7iGVLiL9AjdyoVsaEdiyYKfvdqcAaiGpump_147.webp",
      "risk_score": "0",
      "launch_at": 1748278823,
      "created_at": 1748278823,
      "tx_count_24h": 1613,
      "updated_at": 1748302886,
      "main_pair": "AAS9HrkCDPZQq5PjAsy2Y6MmXr6HCrrEfDe1s7qp4zsz",
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    }
  ]
}
```
````

{% endtab %}
{% endtabs %}

## Get Token Prices

<mark style="color:blue;">`POST`</mark> `https://prod.ave-api.com/v2/tokens/price`

#### Request Body

<table><thead><tr><th>Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>token_ids<mark style="color:red;">*</mark></td><td>array of string</td><td><p>list of token ids, max 200 token ids</p><pre class="language-postman_json"><code class="lang-postman_json"><strong>token_id = {CA}-{chain}
</strong></code></pre></td></tr><tr><td>tvl_min</td><td>int</td><td><p>token min tvl threshold to include into search result </p><p>(<strong>default: 1000</strong>, 0 means no threshold)</p></td></tr><tr><td>tx_24h_volume_min</td><td>int</td><td>token min 24 hour volume threshold to include into search result (<strong>default: 0</strong>, 0 means no threshold)</td></tr></tbody></table>

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": {
    "0x78f5d389f5cdccfc41594abab4b0ed02f31398b3-bsc": {
      "current_price_usd": "0.08204179857619828",
      "price_change_1d": "0.47",
      "price_change_24h": "1.14",
      "tvl": "3566687.259372",
      "tx_volume_u_24h": "210521.343555",
      "token_id": "0x78f5d389f5cdccfc41594abab4b0ed02f31398b3-bsc",
      "updated_at": 1748332901
    },
    "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN-solana": {
      "current_price_usd": "12.866432249296329",
      "price_change_1d": "1.0",
      "price_change_24h": "-0.79",
      "tvl": "392581528.783831",
      "tx_volume_u_24h": "44687539.591042",
      "token_id": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN-solana",
      "updated_at": 1748333069
    }
  }
}
```
````

{% endtab %}
{% endtabs %}

## Get Token Rank Topics

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/ranks/topics`

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": [
    {
      "id": "hot",
      "name_en": "Hot",
      "name_zh": "??"
    },
    {
      "id": "meme",
      "name_en": "Meme",
      "name_zh": "Meme"
    },
    {
      "id": "gainer",
      "name_en": "Gainers",
      "name_zh": "???"
    },
    {
      "id": "solana",
      "name_en": "Solana",
      "name_zh": "Solana"
    },
    {
      "id": "new",
      "name_en": "New",
      "name_zh": "??"
    },
    {
      "id": "bsc",
      "name_en": "BSC",
      "name_zh": "BSC"
    },
    {
      "id": "loser",
      "name_en": "Losers",
      "name_zh": "???"
    },
    {
      "id": "eth",
      "name_en": "Ethereum",
      "name_zh": "Ethereum"
    },
    {
      "id": "base",
      "name_en": "Base",
      "name_zh": "Base"
    },
    {
      "id": "depin",
      "name_en": "Depin",
      "name_zh": "Depin"
    },
    {
      "id": "ai",
      "name_en": "AI",
      "name_zh": "AI"
    },
    {
      "id": "l2",
      "name_en": "L2",
      "name_zh": "L2"
    },
    {
      "id": "gamefi",
      "name_en": "GameFi",
      "name_zh": "GameFi"
    },
    {
      "id": "rwa",
      "name_en": "RWA",
      "name_zh": "RWA"
    },
    {
      "id": "arbitrum",
      "name_en": "Arbitrum",
      "name_zh": "Arbitrum"
    },
    {
      "id": "blast",
      "name_en": "Blast",
      "name_zh": "Blast"
    },
    {
      "id": "polygon",
      "name_en": "Polygon",
      "name_zh": "Polygon"
    },
    {
      "id": "optimism",
      "name_en": "Optimism",
      "name_zh": "Optimism"
    },
    {
      "id": "avalanche",
      "name_en": "Avalanche",
      "name_zh": "Avalanche"
    },
    {
      "id": "merlin",
      "name_en": "Merlin",
      "name_zh": "Merlin"
    }
  ]
}
```
````

{% endtab %}
{% endtabs %}

## Get Rank Token List By Topic

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/ranks?topic={topic}`

#### Query Parameters

| Name                                    | Type   | Description            |
| --------------------------------------- | ------ | ---------------------- |
| topic<mark style="color:red;">\*</mark> | string | topic in rank topics   |
| limit                                   | int    | Default: 200, Max: 300 |

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": [
    {
      "total": "420689899653543.56",
      "launch_price": "0.000000000010634444526215848",
      "current_price_eth": "0.000000005402700316454905",
      "current_price_usd": "0.000014162924534087142",
      "price_change_1d": "2.15",
      "price_change_24h": "-1.0",
      "lock_amount": "0",
      "burn_amount": "6917089958934.084",
      "other_amount": "0",
      "tx_amount_24h": "254267485167.79752",
      "tx_volume_u_24h": "3515062.1907288465",
      "locked_percent": "0.016442222353235",
      "market_cap": "5860233077.961954585371691842957592",
      "fdv": "5860233077.961954585371691842957592",
      "tvl": "53299857.035616",
      "main_pair_tvl": "53299857.035616",
      "token_price_change_5m": "0",
      "token_price_change_1h": "1.8",
      "token_price_change_4h": "2.89",
      "token_price_change_24h": "-1.78",
      "token_tx_volume_usd_5m": "0",
      "token_tx_volume_usd_1h": "122376.071352",
      "token_tx_volume_usd_4h": "404944.750329",
      "token_tx_volume_usd_24h": "3537424.495231",
      "token_buy_volume_u_5m": "0",
      "token_sell_volume_u_5m": "0",
      "token": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
      "chain": "eth",
      "decimal": 18,
      "name": "Pepe",
      "symbol": "PEPE",
      "holders": 439406,
      "appendix": "{\"contractAddress\":\"\",\"tokenName\":\"\",\"symbol\":\"\",\"divisor\":\"\",\"tokenType\":\"\",\"totalSupply\":\"\",\"blueCheckmark\":\"\",\"description\":\"$PEPE. The most memeable memecoin in existence. Let’s make memecoins great again.\",\"website\":\"https://www.pepe.vip/\",\"email\":\"\",\"blog\":\"\",\"reddit\":\"\",\"slack\":\"\",\"facebook\":\"\",\"twitter\":\"https://twitter.com/pepecoineth\",\"btok\":\"\",\"bitcointalk\":\"\",\"github\":\"\",\"telegram\":\"https://t.me/pepecoineth\",\"wechat\":\"\",\"linkedin\":\"\",\"discord\":\"\",\"qq\":\"\",\"whitepaper\":\"\",\"tokenPriceUSD\":\"\"}",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon/eth/0x6982508145454ce325ddbe47a25d4ec3d2311933.png",
      "risk_score": "55",
      "created_at": 1681492871,
      "tx_count_24h": 808,
      "buy_tx": "0.0",
      "sell_tx": "0.0",
      "is_mintable": "0",
      "updated_at": 1748333374,
      "main_pair": "0xa43fe16908251ee70ef74718545e4fe6c5ccec9f",
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    },
    {
      "total": "88886098678.18576",
      "launch_price": "0.000007099322125333869",
      "current_price_eth": "0.000022715404238418447",
      "current_price_usd": "0.0040066563498126215",
      "price_change_1d": "0.5",
      "price_change_24h": "-2.29",
      "lock_amount": "0",
      "burn_amount": "0",
      "other_amount": "0",
      "tx_amount_24h": "714335833.62752",
      "tx_volume_u_24h": "2825521.282848818",
      "locked_percent": "0",
      "market_cap": "356136051.679024237942405569569840",
      "fdv": "356136051.679024237942405569569840",
      "tvl": "33950119.331393",
      "main_pair_tvl": "33950119.331393",
      "token_price_change_5m": "0",
      "token_price_change_1h": "2.19",
      "token_price_change_4h": "1.77",
      "token_price_change_24h": "-2.28",
      "token_tx_volume_usd_5m": "0",
      "token_tx_volume_usd_1h": "64985.458942",
      "token_tx_volume_usd_4h": "301064.588918",
      "token_tx_volume_usd_24h": "2825606.388089",
      "token_buy_volume_u_5m": "0",
      "token_sell_volume_u_5m": "0",
      "token": "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5",
      "chain": "solana",
      "decimal": 5,
      "name": "cat in a dogs world",
      "symbol": "MEW",
      "holders": 175400,
      "intro_en": "cat in a dogs world (MEW)",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon_solana/solana/MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5.png",
      "risk_score": "55",
      "created_at": 1711430534,
      "tx_count_24h": 6489,
      "is_mintable": "0",
      "updated_at": 1748333336,
      "main_pair": "879F697iuDJGMevRkRcnW21fcXiAeLJK1ffsw2ATebce",
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    }
  ]
}
```
````

{% endtab %}
{% endtabs %}

## Get Token Detail

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/tokens/{token-id}`

#### Query Path

| Name                                        | Type   | Description                                                                                                    |
| ------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| token\_id<mark style="color:red;">\*</mark> | string | <p>token\_id = {token}-{chain}<br>eg: <code>6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN-solana</code><br></p> |

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": {
    "token": {
      "total": "999999418.723847",
      "launch_price": "1.2555332002309751",
      "current_price_eth": "0.0729807648723581",
      "current_price_usd": "12.866432249296329",
      "price_change_1d": "1.0",
      "price_change_24h": "-0.75",
      "price_change_1h": "0.5",
      "lock_amount": "800000024.164006",
      "burn_amount": "0",
      "other_amount": "0",
      "tx_amount_24h": "3462619.873997",
      "tx_volume_u_24h": "44291710.669145",
      "locked_percent": "0.8000004998222048",
      "market_cap": "2573278660.004479023302932123689",
      "fdv": "12866424770.346088293892921857663",
      "tvl": "392581528.783831",
      "main_pair_tvl": "392581528.783831",
      "token_price_change_5m": "0",
      "token_price_change_1h": "0.5",
      "token_price_change_4h": "1.71",
      "token_price_change_24h": "-0.79",
      "token_tx_volume_usd_5m": "0",
      "token_tx_volume_usd_1h": "664930.185681",
      "token_tx_volume_usd_4h": "4887883.703225",
      "token_tx_volume_usd_24h": "44687539.591042",
      "token_buy_volume_u_5m": "0",
      "token_sell_volume_u_5m": "0",
      "token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
      "chain": "solana",
      "decimal": 6,
      "name": "OFFICIAL TRUMP",
      "symbol": "TRUMP",
      "holders": 637675,
      "appendix": "{\"contractAddress\":\"\",\"tokenName\":\"OFFICIAL TRUMP\",\"symbol\":\"TRUMP\",\"divisor\":\"\",\"tokenType\":\"\",\"totalSupply\":\"999999810.732535\",\"blueCheckmark\":\"\",\"description\":\"\",\"website\":\"https://gettrumpmemes.com/\",\"email\":\"\",\"blog\":\"\",\"reddit\":\"\",\"slack\":\"\",\"facebook\":\"\",\"twitter\":\"https://x.com/realDonaldTrump/status/1880446012168249386\",\"btok\":\"\",\"bitcointalk\":\"\",\"github\":\"\",\"telegram\":\"\",\"wechat\":\"\",\"linkedin\":\"\",\"discord\":\"\",\"qq\":\"\",\"whitepaper\":\"\",\"tokenPriceUSD\":\"\"}",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon/solana/6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN_1737366143.png",
      "risk_info": "{\"zh-cn\":\"\",\"zh-tw\":\"\",\"en\":\"\"}",
      "risk_score": "55",
      "launch_at": 1737165695,
      "created_at": 1737165695,
      "tx_count_24h": 6029,
      "lock_platform": "Lock",
      "is_mintable": "0",
      "updated_at": 1748333513,
      "main_pair": "9d9mb8kooFfaD3SctgZtkxQypkshx6ezhbKio89ixyy2",
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    },
    "pairs": [
      {
        "reserve0": "10137992.419064",
        "reserve1": "262141736.180064",
        "token0_price_eth": "0.0729807648723581",
        "token0_price_usd": "12.866432249296329",
        "token1_price_eth": "0.005559669791602979",
        "token1_price_usd": "1",
        "price_change": "1.0",
        "price_change_24h": "-0.79",
        "price_change_1h": "0.5",
        "volume_u": "44687539.591042",
        "low_u": "12.365958873075085",
        "high_u": "13.241981148765477",
        "fee": "",
        "total_supply": "",
        "tx_amount": "3493139.9981900007",
        "pair": "9d9mb8kooFfaD3SctgZtkxQypkshx6ezhbKio89ixyy2",
        "chain": "solana",
        "amm": "meteora",
        "token0_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "token0_symbol": "TRUMP",
        "token0_decimal": 6,
        "token1_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "token1_symbol": "USDC",
        "token1_decimal": 6,
        "target_token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "price_change_1d": "1.0",
        "created_at": 1737196773,
        "tx_count": 6098,
        "updated_at": 1748333513,
        "market_cap": "2573278660.004479023302932123689",
        "fdv": "12866424770.346088293892921857663",
        "is_fake": false
      },
      {
        "reserve0": "617777.483606",
        "reserve1": "9260146.594104",
        "token0_price_eth": "0.07334472578084972",
        "token0_price_usd": "12.802764624129294",
        "token1_price_eth": "0.005559669791602979",
        "token1_price_usd": "1",
        "price_change": "1.16",
        "price_change_24h": "-1.84",
        "price_change_1h": "0",
        "volume_u": "1725.599532",
        "low_u": "12.3954797539764",
        "high_u": "13.160712779007353",
        "fee": "",
        "total_supply": "",
        "tx_amount": "135.270427",
        "pair": "A8nPhpCJqtqHdqUk35Uj9Hy2YsGXFkCZGuNwvkD3k7VC",
        "chain": "solana",
        "amm": "meteora",
        "token0_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "token0_symbol": "TRUMP",
        "token0_decimal": 6,
        "token1_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "token1_symbol": "USDC",
        "token1_decimal": 6,
        "target_token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "price_change_1d": "1.16",
        "created_at": 1737165695,
        "tx_count": 31,
        "updated_at": 1748332999,
        "market_cap": "2560545173.518009127585004082254",
        "fdv": "12802757182.187525521633009074018",
        "is_fake": false
      },
      {
        "reserve0": "188102.597403",
        "reserve1": "6419.543503378",
        "token0_price_eth": "0.07331182614299207",
        "token0_price_usd": "12.840669999253898",
        "token1_price_eth": "0.9998638827505575",
        "token1_price_usd": "175.43295543498508",
        "price_change": "11.72",
        "price_change_24h": "8.46",
        "price_change_1h": "12.37",
        "volume_u": "5330.466523",
        "low_u": "13.813618538187802",
        "high_u": "13.85217459824488",
        "fee": "",
        "total_supply": "",
        "tx_amount": "418.82393",
        "pair": "4CTUHtiHrPHFT4Zc1qNScrposmM7xfupU7EVDWCR7PZw",
        "chain": "solana",
        "amm": "meteora",
        "token0_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "token0_symbol": "TRUMP",
        "token0_decimal": 6,
        "token1_address": "So11111111111111111111111111111111111111112",
        "token1_symbol": "SOL",
        "token1_decimal": 9,
        "target_token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "price_change_1d": "11.72",
        "created_at": 1737165696,
        "tx_count": 39,
        "updated_at": 1748333496,
        "market_cap": "2568126225.593493585190113510218",
        "fdv": "12840662535.278638891181300305606",
        "is_fake": false
      },
      {
        "reserve0": "44886.398847",
        "reserve1": "2350.955434601",
        "token0_price_eth": "0.0729807648723581",
        "token0_price_usd": "12.866432249296329",
        "token1_price_eth": "1.0003501709065277",
        "token1_price_usd": "176.17532839847297",
        "price_change": "0.89",
        "price_change_24h": "-0.9",
        "price_change_1h": "0.32",
        "volume_u": "330316.473119",
        "low_u": "12.399392346728145",
        "high_u": "13.263573257901978",
        "fee": "",
        "total_supply": "",
        "tx_amount": "25804.314809999996",
        "pair": "71HuFmuYAFEFUna2x2R4HJjrFNQHGuagW3gUMFToL9tk",
        "chain": "solana",
        "amm": "meteora",
        "token0_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "token0_symbol": "TRUMP",
        "token0_decimal": 6,
        "token1_address": "So11111111111111111111111111111111111111112",
        "token1_symbol": "SOL",
        "token1_decimal": 9,
        "target_token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "price_change_1d": "0.89",
        "created_at": 1737175014,
        "tx_count": 1161,
        "updated_at": 1748333505,
        "market_cap": "2573278660.004479023302932123689",
        "fdv": "12866424770.346088293892921857663",
        "is_fake": false
      },
      {
        "reserve0": "25553.586817",
        "reserve1": "1673.536089451",
        "token0_price_eth": "0.07306239332704488",
        "token0_price_usd": "12.867157396546899",
        "token1_price_eth": "0.9996963072970214",
        "token1_price_usd": "176.3237397776064",
        "price_change": "0.8",
        "price_change_24h": "-0.3",
        "price_change_1h": "0.64",
        "volume_u": "34195.701934",
        "low_u": "12.399217207162334",
        "high_u": "13.240225324047264",
        "fee": "",
        "total_supply": "",
        "tx_amount": "2667.672565",
        "pair": "6XMrsTeFC8gYmVasKaBuVwU4fyAVPJLHd8jno82JBhS5",
        "chain": "solana",
        "amm": "meteora",
        "token0_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "token0_symbol": "TRUMP",
        "token0_decimal": 6,
        "token1_address": "So11111111111111111111111111111111111111112",
        "token1_symbol": "SOL",
        "token1_decimal": 9,
        "target_token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "price_change_1d": "0.8",
        "created_at": 1737166919,
        "tx_count": 199,
        "updated_at": 1748333513,
        "market_cap": "2573423689.015559756619418483059",
        "fdv": "12867149917.175147489723065200453",
        "is_fake": false
      }
    ],
    "is_audited": true
  }
}
```
````

{% endtab %}
{% endtabs %}

## Get Kine Data By Pair

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/klines/pair/{pair-id}?interval={interval}&size={size}`

#### Query Path & Parameters

| Name                                       | Type   | Description                                                                                                                                                                                                                      |
| ------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pair\_id<mark style="color:red;">\*</mark> | string | <p>pair\_id = {pair}-{chain}<br>eg: <code>2prhzdRwWzas2f4g5AAjyRUBcQcdajxd8NAzKcqhv76P-solana</code></p>                                                                                                                         |
| category                                   | string | <p>default is <code>u</code><br><code>u</code> refers to target token USDT price<br><code>r</code> refers to target token to base token relative price<br><code>m</code> refers to target token to main token relative price</p> |
| interval                                   | int    | The time interval of K-Line, 1,5,15,30,60,120,240,1440,4320,10080,43200,525600,2628000                                                                                                                                           |
| limit                                      | int    | The number of records need to return                                                                                                                                                                                             |
| from\_time                                 | int    | start time in unix epoch, default -1                                                                                                                                                                                             |
| to\_time                                   | int    | end time in unix epoch, default now                                                                                                                                                                                              |

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": {
    "points": [
      {
        "open": "12.836103918554272",
        "high": "12.836103918554272",
        "low": "12.827706847270022",
        "close": "12.827706847270022",
        "volume": "0.005657",
        "time": 1748331540
      },
      {
        "open": "12.827706847270022",
        "high": "12.836359926949804",
        "low": "12.827706847270022",
        "close": "12.836359926949804",
        "volume": "149.839523",
        "time": 1748332020
      },
      {
        "open": "12.836359926949804",
        "high": "12.839977726756748",
        "low": "12.836359926949804",
        "close": "12.839977726756748",
        "volume": "48.904689",
        "time": 1748332260
      },
      {
        "open": "12.839977726756748",
        "high": "12.843838945997273",
        "low": "12.839977726756748",
        "close": "12.843838945997273",
        "volume": "50.022232",
        "time": 1748332320
      },
      {
        "open": "12.843838945997273",
        "high": "12.843838945997273",
        "low": "12.823454586637311",
        "close": "12.823454586637311",
        "volume": "116.16806",
        "time": 1748332620
      },
      {
        "open": "12.823454586637311",
        "high": "12.880510657336906",
        "low": "12.823454586637311",
        "close": "12.865735754389533",
        "volume": "362.76989999999995",
        "time": 1748332980
      }
    ],
    "total_count": 6,
    "to_time": 1748333774,
    "limit": 5,
    "interval": 1,
    "pair_id": "6XMrsTeFC8gYmVasKaBuVwU4fyAVPJLHd8jno82JBhS5-solana",
    "target_token_id": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN-solana"
  }
}
```
````

{% endtab %}
{% endtabs %}

## Get Kine Data By Token

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/klines/token/{token-id}?interval={interval}&size={size}`

#### Query Path & Parameters

| Name                                        | Type   | Description                                                                                                                 |
| ------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| token\_id<mark style="color:red;">\*</mark> | string | <p>token\_id = {token}-{chain}<br>eg: <code>6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN-solana</code></p>                  |
| interval                                    | int    | <p>The time interval of K-Line in minutes:</p><p><code>1,5,15,30,60,120,240,1440,4320,10080,43200,525600,2628000</code></p> |
| limit                                       | int    | The number of records need to return                                                                                        |
| from\_time                                  | int    | start time in unix epoch, default -1                                                                                        |
| to\_time                                    | int    | end time in unix epoch, default now                                                                                         |

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": {
    "points": [
      {
        "open": "12.840581539160503",
        "high": "12.840581539160503",
        "low": "12.802742565058404",
        "close": "12.80290508389682",
        "volume": "178.881744",
        "time": 1748332500
      },
      {
        "open": "12.80290508389682",
        "high": "12.867161769288016",
        "low": "12.80290508389682",
        "close": "12.86715733920441",
        "volume": "487.593602",
        "time": 1748332800
      },
      {
        "open": "12.86715733920441",
        "high": "12.867209929066671",
        "low": "12.867156562934094",
        "close": "12.867157396546899",
        "volume": "304189.835493",
        "time": 1748332860
      },
      {
        "open": "12.867157396546899",
        "high": "12.867157396546899",
        "low": "12.866519767978499",
        "close": "12.866519767978499",
        "volume": "2.843681",
        "time": 1748332980
      },
      {
        "open": "12.866519767978499",
        "high": "12.866519767978499",
        "low": "12.866432249296329",
        "close": "12.866432249296329",
        "volume": "645.152073",
        "time": 1748333040
      },
      {
        "open": "12.866432249296329",
        "high": "12.904138292299633",
        "low": "12.866432249296329",
        "close": "12.904138292299633",
        "volume": "0.073902",
        "time": 1748334060
      }
    ],
    "total_count": 6,
    "to_time": 1748334122,
    "limit": 5,
    "interval": 1,
    "pair_id": "9d9mb8kooFfaD3SctgZtkxQypkshx6ezhbKio89ixyy2-solana",
    "target_token_id": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN-solana"
  }
}
```
````

{% endtab %}
{% endtabs %}

## Get Token Top100 Holders

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/tokens/top100/{token-id}`

#### Query Path & Parameters

| Name                                        | Type   | Description                                                                                                |
| ------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| token\_id<mark style="color:red;">\*</mark> | string | <p>token\_id = {token}-{chain}<br>eg: <code>6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN-solana</code></p> |
| limit                                       | int    | <p>Default: 100, Max: 100<br><em>NOTE: this param always 100 for bsc and solana chain</em></p>             |

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": [
    {
      "holder": "2RH6rUTPBJ9rUDPpuV9b8z1YL56k1tYU6Uk5ZoaEFFSK",
      "remark": "",
      "balance_ratio": 0.8000004891852127,
      "balance_usd": 10293151176.366684,
      "main_coin_balance": 5.613352647,
      "avg_purchase_price": 0,
      "avg_sale_price": 0,
      "realized_profit": 0,
      "unrealized_profit": 0,
      "total_profit": 0,
      "realized_profit_ratio": 0,
      "unrealized_profit_ratio": 0,
      "total_profit_ratio": 0,
      "transfer_in": 24.164006,
      "transfer_out": 0,
      "max_single_purchase_usd": 0,
      "max_single_sold_usd": 0,
      "max_txn_usd": 0,
      "total_transfer_in": 245,
      "total_transfer_out": 0,
      "total_transfer_in_usd": 487.8205924642751,
      "last_txn_time": "2025-05-16T13:14:26Z",
      "age": "2025-01-18T12:29:38Z",
      "first_purchase_time": null,
      "token_first_transfer_in_from": "FyEHMgkoyCBULiDRFLDNTXAX1pyNcVfnQRLN23vgVcVZ",
      "token_first_transfer_in_time": "2025-01-18T12:29:38Z",
      "sol_first_transfer_in_from": "DY5qh4bSR2R21xN9DacWWVySDfimYDqJvjkRj7C1JKmY",
      "sol_first_transfer_in_time": "2025-01-18T02:32:45Z",
      "address": "2RH6rUTPBJ9rUDPpuV9b8z1YL56k1tYU6Uk5ZoaEFFSK",
      "addr_alias": "",
      "amount_cur": 800000024.164006,
      "cost_cur": 0,
      "sell_amount_cur": 0,
      "sell_volume_cur": 0,
      "buy_amount_cur": 0,
      "buy_volume_cur": 0,
      "buy_tx_count_cur": 0,
      "sell_tx_count_cur": 0,
      "trade_first_at": 1737203378,
      "trade_last_at": 0
    },
    {
      "holder": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
      "remark": "",
      "balance_ratio": 0.024602102533616516,
      "balance_usd": 316541257.23460793,
      "main_coin_balance": 6070871.943077467,
      "avg_purchase_price": 0,
      "avg_sale_price": 0,
      "realized_profit": 0,
      "unrealized_profit": 0,
      "total_profit": 0,
      "realized_profit_ratio": 0,
      "unrealized_profit_ratio": 0,
      "total_profit_ratio": 0,
      "transfer_in": 78602088.233001,
      "transfer_out": 54000000,
      "max_single_purchase_usd": 0,
      "max_single_sold_usd": 0,
      "max_txn_usd": 0,
      "total_transfer_in": 11,
      "total_transfer_out": 6,
      "total_transfer_in_usd": 2192395586.755653,
      "last_txn_time": "2025-05-10T01:42:25Z",
      "age": "2025-01-22T10:22:03Z",
      "first_purchase_time": null,
      "token_first_transfer_in_from": "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9",
      "token_first_transfer_in_time": "2025-01-22T10:22:03Z",
      "sol_first_transfer_in_from": "",
      "sol_first_transfer_in_time": "2024-10-29T08:19:35Z",
      "address": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
      "addr_alias": "",
      "amount_cur": 24602088.233001,
      "cost_cur": 0,
      "sell_amount_cur": 0,
      "sell_volume_cur": 0,
      "buy_amount_cur": 0,
      "buy_volume_cur": 0,
      "buy_tx_count_cur": 0,
      "sell_tx_count_cur": 0,
      "trade_first_at": 1737541323,
      "trade_last_at": 0
    }
  ]
}
```
````

{% endtab %}
{% endtabs %}

## Get Swap Transactions By Pair

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/txs/{pair-id}?limit={limit}&size={size}&to_time={to_time}`

#### Query Parameters

| Name                                       | Type   | Description                                                                                              |
| ------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------------- |
| pair\_id<mark style="color:red;">\*</mark> | string | <p>pair\_id = {pair}-{chain}<br>eg: <code>2prhzdRwWzas2f4g5AAjyRUBcQcdajxd8NAzKcqhv76P-solana</code></p> |
| limit                                      | int    | The number of records need to return                                                                     |
| from\_time                                 | int    | start time in unix epoch, default -1                                                                     |
| to\_time                                   | int    | end time in unix epoch, default now                                                                      |
| sort                                       | string | <p>asc, desc<br>Default: asc</p>                                                                         |

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": {
    "txs": [
      {
        "amount_usd": "3.2132175046587855460003311236505396664143",
        "pair_liquidity_usd": "295173.7136571566987915893788567700539715588093",
        "from_token_price_usd": "12.8657357543895329854422016069293022155762",
        "from_token_amount": "0.24975",
        "from_token_reserve": "25553.586817",
        "to_token_price_usd": "176.3772622041200293097062967717647552490234",
        "to_token_amount": "0.018217867",
        "to_token_reserve": "1673.536089451",
        "tx_time": 1748333018,
        "chain": "solana",
        "tx_hash": "33tFHybwPRz83asvY6khbtvfDsoc3s2yP3pGmxyahVu3G34VXmUcDpNCsVP5AZjqg57TLjXAWi1RY1rZLvrBbSdH",
        "block_number": 342763431,
        "amm": "meteora",
        "sender_address": "EATSUzfFtzoXnWVMmavTJQry1krNboTBx7ecCeUWKp9r",
        "to_address": "DxDLtnvrE2B4PFLGm1r5szYad8rUvLH8Sqro8ss8KqVT",
        "pair_address": "6XMrsTeFC8gYmVasKaBuVwU4fyAVPJLHd8jno82JBhS5",
        "from_token_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "from_token_symbol": "TRUMP",
        "to_token_address": "So11111111111111111111111111111111111111112",
        "to_token_symbol": "SOL",
        "wallet_address": "EATSUzfFtzoXnWVMmavTJQry1krNboTBx7ecCeUWKp9r"
      },
      {
        "amount_usd": "0.8992049284796316822495043652452295646071",
        "pair_liquidity_usd": "294078.5521984705817651821732283679011743515730",
        "from_token_price_usd": "12.8168552193567588659561806707642972469330",
        "from_token_amount": "0.070158",
        "from_token_reserve": "25553.656975",
        "to_token_price_usd": "175.7233998460536383845465024933218955993652",
        "to_token_amount": "0.005117161",
        "to_token_reserve": "1673.530972290",
        "tx_time": 1748334877,
        "chain": "solana",
        "tx_hash": "5zNHuWnE21cNhN68kLsD1YkmcPSchoMwuoPtbQVJgKvtDpvrPRSy46GL717LMJsdvwByJecbAKdVMEYX4S6CtxHj",
        "block_number": 342768159,
        "amm": "meteora",
        "sender_address": "CTQXBfh7LCTaNAZyfSBiYDSREJapEwpMvu8ALvCiDucu",
        "to_address": "CzzicPZWWgXviWRBPUaWSaJkjYmQQssgfrDhCpcc7ibr",
        "pair_address": "6XMrsTeFC8gYmVasKaBuVwU4fyAVPJLHd8jno82JBhS5",
        "from_token_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "from_token_symbol": "TRUMP",
        "to_token_address": "So11111111111111111111111111111111111111112",
        "to_token_symbol": "SOL",
        "wallet_address": "CTQXBfh7LCTaNAZyfSBiYDSREJapEwpMvu8ALvCiDucu"
      }
    ],
    "total_count": 2,
    "to_time": 1748334985,
    "limit": 2,
    "pair_id": "6XMrsTeFC8gYmVasKaBuVwU4fyAVPJLHd8jno82JBhS5-solana"
  }
}
```
````

{% endtab %}
{% endtabs %}

## Get Supported Chains

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/supported_chains`

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": [
    {
      "chain_id": "56",
      "name": "BSC",
      "chain": "bsc",
      "description": "Binance Smart Chain",
      "rpc_url": "https://api.dryespah.com/ave_nodes/rpc/bsc/sendFastSwapTx",
      "block_explorer_url": "https://bscscan.com",
      "case_sensitive": false,
      "only_native_coin": false
    },
    {
      "chain_id": "solana",
      "name": "Solana",
      "chain": "solana",
      "description": "Solana",
      "rpc_url": "https://api.dryespah.com/ave_nodes/rpc/solana/sendFastSwapTx",
      "block_explorer_url": "https://solscan.io",
      "case_sensitive": true,
      "only_native_coin": false
    }
  ]
}
```
````

{% endtab %}
{% endtabs %}

## Get Chain Main Tokens

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/tokens/main?chain={chain_name}`

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": [
    {
      "total": "571367938",
      "launch_price": "158.5995241871530531324345757335448057097542",
      "current_price_eth": "1.0000506231772368",
      "current_price_usd": "175.85266249240544",
      "price_change_1d": "0.43",
      "price_change_24h": "-1.09",
      "lock_amount": "0",
      "burn_amount": "0",
      "other_amount": "128242257",
      "tx_amount_24h": "1386389.612344928",
      "tx_volume_u_24h": "242894331.283494",
      "locked_percent": "0",
      "market_cap": "77924830822.61031792810464",
      "fdv": "77924830822.61031792810464",
      "tvl": "46179051.905655",
      "main_pair_tvl": "46179051.905655",
      "token_price_change_5m": "0.01",
      "token_price_change_1h": "0.29",
      "token_price_change_4h": "1.12",
      "token_price_change_24h": "-1.09",
      "token_tx_volume_usd_5m": "963255.257277",
      "token_tx_volume_usd_1h": "14186582.935249",
      "token_tx_volume_usd_4h": "44432827.912976",
      "token_tx_volume_usd_24h": "242894331.283494",
      "token_buy_volume_u_5m": "507044.726743",
      "token_sell_volume_u_5m": "456210.530534",
      "token": "So11111111111111111111111111111111111111112",
      "chain": "solana",
      "decimal": 9,
      "name": "Wrapped SOL",
      "symbol": "WSOL",
      "holders": 1917958,
      "appendix": "{\"website\": \"https://solana.com/\", \"medium\": \"https://medium.com/solana-labs\", \"reddit\": \"https://reddit.com/r/solana\", \"twitter\": \"https://twitter.com/solana\", \"discord\": \"https://discordapp.com/invite/pquxPsq\"}",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon/solana/So11111111111111111111111111111111111111112.png",
      "risk_score": "20",
      "created_at": 0,
      "tx_count_24h": 35471,
      "is_mintable": "0",
      "updated_at": 1748335213,
      "main_pair": "Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE",
      "token_buy_tx_count_5m": 91,
      "token_sell_tx_count_5m": 52,
      "token_buyers_5m": 21,
      "token_sellers_5m": 17,
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    },
    {
      "total": "2389929354.727879",
      "launch_price": "0.9989927473809430906022105030410174677164",
      "current_price_eth": "0.005688352865717098",
      "current_price_usd": "1.0002613602245343",
      "price_change_1d": "-0.01",
      "price_change_24h": "-0.01",
      "lock_amount": "0",
      "burn_amount": "0",
      "other_amount": "0",
      "tx_amount_24h": "2161809.2181080002",
      "tx_volume_u_24h": "2162675.611962",
      "locked_percent": "0",
      "market_cap": "2390553987.2006517931687160017497",
      "fdv": "2390553987.2006517931687160017497",
      "tvl": "8668890.225753",
      "main_pair_tvl": "8668890.225753",
      "token_price_change_5m": "0.0",
      "token_price_change_1h": "0.0",
      "token_price_change_4h": "0.0",
      "token_price_change_24h": "-0.01",
      "token_tx_volume_usd_5m": "1251.605313",
      "token_tx_volume_usd_1h": "34712.443096",
      "token_tx_volume_usd_4h": "324540.709848",
      "token_tx_volume_usd_24h": "2162675.611962",
      "token_buy_volume_u_5m": "57.294927",
      "token_sell_volume_u_5m": "1194.310386",
      "token": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
      "chain": "solana",
      "decimal": 6,
      "name": "USDT",
      "symbol": "USDT",
      "holders": 2029411,
      "appendix": "{\"website\": \"https://tether.to/\", \"whitepaper\": \"https://tether.to/wp-content/uploads/2016/06/TetherWhitePaper.pdf\", \"twitter\": \"https://twitter.com/Tether_to\", \"facebook\": \"https://www.facebook.com/tether.to\", \"coingecko\": \"https://www.coingecko.com/en/categories/stablecoins\"}",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon/solana/Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB.png",
      "risk_score": "20",
      "created_at": 0,
      "tx_count_24h": 3524,
      "is_mintable": "1",
      "updated_at": 1748335210,
      "main_pair": "BZtgQEyS6eXUXicYPHecYQ7PybqodXQMvkjUbP4R8mUU",
      "token_buy_tx_count_5m": 2,
      "token_sell_tx_count_5m": 5,
      "token_buyers_5m": 2,
      "token_sellers_5m": 5,
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    },
    {
      "total": "483499.706056",
      "launch_price": "320.4947717633607",
      "current_price_eth": "6.191970424941277",
      "current_price_usd": "1088.3865930024401",
      "price_change_1d": "0.61",
      "price_change_24h": "-1.88",
      "lock_amount": "0",
      "burn_amount": "1413.670699",
      "other_amount": "0",
      "tx_amount_24h": "6.644578",
      "tx_volume_u_24h": "7136.554886",
      "locked_percent": "0.0029238294900563",
      "market_cap": "524695977.5562591068358746157",
      "fdv": "524695977.5562591068358746157",
      "tvl": "168770.564844",
      "main_pair_tvl": "168770.564844",
      "token_price_change_5m": "0.7",
      "token_price_change_1h": "0.76",
      "token_price_change_4h": "1.56",
      "token_price_change_24h": "-1.88",
      "token_tx_volume_usd_5m": "139.632748",
      "token_tx_volume_usd_1h": "412.753057",
      "token_tx_volume_usd_4h": "981.9406",
      "token_tx_volume_usd_24h": "7136.554886",
      "token_buy_volume_u_5m": "52.682971",
      "token_sell_volume_u_5m": "86.94977732787196",
      "token": "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk",
      "chain": "solana",
      "decimal": 6,
      "name": "Wrapped Ethereum (Sollet)",
      "symbol": "SOETH",
      "holders": 17060,
      "appendix": "{\"website\": \"https://www.ethereum.org/\", \"twitter\": \"https://twitter.com/ethereum\", \"discord\": \"https://discord.com/invite/CetY6Y4\"}",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon/solana/2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk.png",
      "risk_score": "80",
      "created_at": 0,
      "tx_count_24h": 258,
      "lock_platform": "Blackhole/????1",
      "is_mintable": "0",
      "updated_at": 1748335132,
      "main_pair": "9Hm8QX7ZhE9uB8L2arChmmagZZBtBmnzBbpfxzkQp85D",
      "token_buy_tx_count_5m": 5,
      "token_sell_tx_count_5m": 1,
      "token_buyers_5m": 5,
      "token_sellers_5m": 1,
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    },
    {
      "total": "10434401207.449836",
      "launch_price": "0",
      "current_price_eth": "0",
      "current_price_usd": "1",
      "price_change_1d": "0",
      "lock_amount": "0",
      "burn_amount": "0",
      "other_amount": "0",
      "tx_amount_24h": "0",
      "tx_volume_u_24h": "0",
      "locked_percent": "0",
      "market_cap": "10434401207.449836",
      "fdv": "10434401207.449836",
      "token_price_change_5m": "0",
      "token_price_change_1h": "0",
      "token_price_change_4h": "0",
      "token_price_change_24h": "0",
      "token_tx_volume_usd_5m": "0",
      "token_tx_volume_usd_1h": "0",
      "token_tx_volume_usd_4h": "0",
      "token_tx_volume_usd_24h": "0",
      "token_buy_volume_u_5m": "0",
      "token_sell_volume_u_5m": "0",
      "token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "chain": "solana",
      "decimal": 6,
      "name": "USD Coin",
      "symbol": "USDC",
      "holders": 4365063,
      "appendix": "{\"website\": \"https://www.circle.com/en/usdc\", \"medium\": \"https://medium.com/centre-blog\", \"github\": \"https://github.com/centrehq\", \"coingecko\": \"https://www.coingecko.com/en/categories/stablecoins\", \"whitepaper\": \"https://f.hubspotusercontent30.net/hubfs/9304636/PDF/centre-whitepaper.pdf\", \"twitter\": \"https://twitter.com/circlepay\"}",
      "risk_level": 1,
      "logo_url": "https://www.iconaves.com/token_icon/solana/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v.png",
      "risk_score": "50",
      "created_at": 0,
      "is_mintable": "1",
      "updated_at": 1734432961,
      "has_mint_method": false,
      "is_lp_not_locked": false,
      "has_not_renounced": false,
      "has_not_audited": false,
      "has_not_open_source": false,
      "is_in_blacklist": false,
      "is_honeypot": false,
      "ave_risk_level": 0
    }
  ]
}
```
````

{% endtab %}
{% endtabs %}

## Get Chain Trending List

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/tokens/trending?chain={chain_name}`

#### Query Parameters

| Name                                    | Type   | Description              |
| --------------------------------------- | ------ | ------------------------ |
| chain<mark style="color:red;">\*</mark> | string | chain name               |
| current\_page                           | int    | Default: 0, Start from 0 |
| page\_size                              | int    | Default: 50              |

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": {
    "current_page_size": 2,
    "next_page": 1,
    "tokens": [
      {
        "total": "1000000000000",
        "launch_price": "0.00000012137729641011708",
        "current_price_eth": "0.000000013228648217517789",
        "current_price_usd": "0.0000023262527556344555",
        "lock_amount": "0",
        "burn_amount": "0",
        "other_amount": "0",
        "market_cap": "2323514.8761371093000000000000",
        "fdv": "2323514.8761371093000000000000",
        "tvl": "377257.37590008787750069429000",
        "token_price_change_5m": "-0.16",
        "token_price_change_1h": "0.9",
        "token_price_change_4h": "14.52",
        "token_price_change_24h": "1810.26",
        "token_tx_volume_usd_5m": "340762.585183",
        "token_tx_volume_usd_1h": "3189972.393871",
        "token_tx_volume_usd_4h": "10358766.053819",
        "token_tx_volume_usd_24h": "82203724.448985",
        "token": "84fb2MuMr6e2ziwqNJRwZqovFmnwTVdUXjxuLh3Fpump",
        "chain": "solana",
        "decimal": 6,
        "name": "BARRON TRUMP",
        "symbol": "BTRUMP",
        "holders": 4474,
        "logo_url": "",
        "launch_at": 1748269850,
        "created_at": 1748269849,
        "updated_at": 1748335504,
        "token_tx_count_5m": 3390,
        "token_tx_count_1h": 31400,
        "token_tx_count_4h": 121180,
        "token_tx_count_24h": 576212,
        "token_buy_tx_count_5m": 1710,
        "token_buy_tx_count_1h": 15949,
        "token_buy_tx_count_4h": 60227,
        "token_buy_tx_count_24h": 299843,
        "token_sell_tx_count_5m": 1795,
        "token_sell_tx_count_1h": 16700,
        "token_sell_tx_count_4h": 63181,
        "token_sell_tx_count_24h": 316435,
        "token_makers_5m": 154,
        "token_makers_1h": 895,
        "token_makers_4h": 1896,
        "token_makers_24h": 13093,
        "token_buyers_5m": 145,
        "token_buyers_1h": 862,
        "token_buyers_4h": 1884,
        "token_buyers_24h": 13078,
        "token_sellers_5m": 148,
        "token_sellers_1h": 818,
        "token_sellers_4h": 1616,
        "token_sellers_24h": 12476,
        "has_mint_method": false,
        "is_lp_not_locked": true,
        "has_not_renounced": true,
        "has_not_audited": true,
        "has_not_open_source": false,
        "is_in_blacklist": false,
        "is_honeypot": false,
        "ave_risk_level": 1
      },
      {
        "total": "999999418.723847",
        "launch_price": "1.2555332002309751",
        "current_price_eth": "0.07303311547245597",
        "current_price_usd": "12.832432432432432",
        "lock_amount": "800000024.164006",
        "burn_amount": "0",
        "other_amount": "0",
        "market_cap": "2566478717.216554151351613163312",
        "fdv": "12832424973.245474043243494605904",
        "tvl": "523490055.150664",
        "token_price_change_5m": "0",
        "token_price_change_1h": "-0.06",
        "token_price_change_4h": "0.95",
        "token_price_change_24h": "-0.81",
        "token_tx_volume_usd_5m": "0",
        "token_tx_volume_usd_1h": "732406.963434",
        "token_tx_volume_usd_4h": "4894314.665888",
        "token_tx_volume_usd_24h": "44304676.405271",
        "token": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "chain": "solana",
        "decimal": 6,
        "name": "OFFICIAL TRUMP",
        "symbol": "TRUMP",
        "holders": 637672,
        "appendix": "{\"contractAddress\":\"\",\"tokenName\":\"OFFICIAL TRUMP\",\"symbol\":\"TRUMP\",\"divisor\":\"\",\"tokenType\":\"\",\"totalSupply\":\"999999810.732535\",\"blueCheckmark\":\"\",\"description\":\"\",\"website\":\"https://gettrumpmemes.com/\",\"email\":\"\",\"blog\":\"\",\"reddit\":\"\",\"slack\":\"\",\"facebook\":\"\",\"twitter\":\"https://x.com/realDonaldTrump/status/1880446012168249386\",\"btok\":\"\",\"bitcointalk\":\"\",\"github\":\"\",\"telegram\":\"\",\"wechat\":\"\",\"linkedin\":\"\",\"discord\":\"\",\"qq\":\"\",\"whitepaper\":\"\",\"tokenPriceUSD\":\"\"}",
        "logo_url": "https://www.iconaves.com/token_icon/solana/6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN_1737366143.png",
        "launch_at": 1737165695,
        "created_at": 1737165695,
        "updated_at": 1748335335,
        "token_tx_count_1h": 180,
        "token_tx_count_4h": 858,
        "token_tx_count_24h": 6053,
        "token_buy_tx_count_1h": 104,
        "token_buy_tx_count_4h": 428,
        "token_buy_tx_count_24h": 3022,
        "token_sell_tx_count_1h": 76,
        "token_sell_tx_count_4h": 430,
        "token_sell_tx_count_24h": 3031,
        "token_makers_1h": 44,
        "token_makers_4h": 127,
        "token_makers_24h": 320,
        "token_buyers_1h": 30,
        "token_buyers_4h": 88,
        "token_buyers_24h": 218,
        "token_sellers_1h": 23,
        "token_sellers_4h": 117,
        "token_sellers_24h": 254,
        "has_mint_method": false,
        "is_lp_not_locked": true,
        "has_not_renounced": true,
        "has_not_audited": true,
        "has_not_open_source": false,
        "is_in_blacklist": false,
        "is_honeypot": false,
        "ave_risk_level": 0
      }
    ],
    "total": 2400
  }
}
```
````

{% endtab %}
{% endtabs %}

## Get Contract Risk Detection Report

<mark style="color:blue;">`GET`</mark> `https://prod.ave-api.com/v2/contracts/{token-id}`

#### Query Path

<table><thead><tr><th width="155">Params</th><th>Description</th></tr></thead><tbody><tr><td>token_id<mark style="color:red;">*</mark></td><td>token_id = {token}-{chain}<br>eg: </td></tr></tbody></table>

#### Response Body

{% tabs %}
{% tab title="200: OK Success" %}

````json
```json
{
  "status": 1,
  "msg": "SUCCESS",
  "data_type": 1,
  "data": {
    "analysis_big_wallet": "0",
    "analysis_creator_gt_5percent": 0,
    "analysis_lp_creator_gt_5percent": 0,
    "analysis_lp_current_adequate": "1",
    "analysis_lp_current_volume": 3597868,
    "analysis_scam_wallet": "0",
    "anti_whale_modifiable": "0",
    "approve_gas": "0.00157924303170942814022",
    "burn_amount": 0,
    "buy_gas": "0.00878980153238541123238",
    "buy_tax": 0,
    "can_take_back_ownership": "0",
    "cannot_buy": "0",
    "cannot_sell_all": "0",
    "chain": "bsc",
    "creator_address": "0xb779a009e99512ca46bc76a4df26e6dd58ee22ea",
    "creator_balance": "0",
    "creator_percent": "0.000000",
    "creator_tx": "0x04836f42856dd60bb3ed027de95cbdc4d4e3304e83280a6e66e0306862d5866e",
    "decimal": "18",
    "dex": [
      {
        "amm": "cakev2",
        "liquidity": "3597868.379115746024466106735652563251533376",
        "name": "Cakev2: SKYAI/WBNB",
        "pair": "0xbc42145d5a574ede9b8860fca2a49eb7b239efa5"
      },
      {
        "amm": "pancakev3",
        "liquidity": "2395409.031892618393067995684857086647070444",
        "name": "Pancakev3: SKYAI/USDT",
        "pair": "0x69b86059c5fb3a44355937e7b505a659443b9a22"
      },
      {
        "amm": "pancakev3",
        "liquidity": "87362.80636122359752369065467378038049757",
        "name": "Pancakev3: SKYAI/WBNB",
        "pair": "0x1c67a1cf31e75213b33d7ee467182a8a4280de22"
      },
      {
        "amm": "pancakev3",
        "liquidity": "52512.16055235800141675131802432327226345",
        "name": "Pancakev3: SKYAI/USDT",
        "pair": "0xc20e8fe55f8cef2656ae2a251bf097ca9279f15e"
      },
      {
        "amm": "pancakev3",
        "liquidity": "97.23829881306028802091820070833771848",
        "name": "Pancakev3: SKYAI/WBNB",
        "pair": "0x4861a349c0494cc92b99d46b44a0c4403c16f087"
      },
      {
        "amm": "pancakev3",
        "liquidity": "23.84887938848877966778571321232474202",
        "name": "Pancakev3: SKYAI/WBNB",
        "pair": "0x4085f0ff7d7b736d42ec369e53f841b30f7ee0e1"
      },
      {
        "amm": "pancakev3",
        "liquidity": "0.12962567011389237412785782697419762",
        "name": "Pancakev3: SKYAI/WBNB",
        "pair": "0xbcc5cf85fbef7a828c5f4f5682797d656f3edd46"
      },
      {
        "amm": "uniswapv3",
        "liquidity": "0.0000000000000000010001871591706164021928771035163663327693939208984375",
        "name": "Uniswapv3: SKYAI/USDT",
        "pair": "0x8c8dbe9ee9126c1f0def2960c61362a0da8f5247"
      }
    ],
    "err_code": "0",
    "err_msg": "",
    "external_call": "0",
    "has_black_method": 0,
    "has_code": 1,
    "has_mint_method": 0,
    "has_owner_removed_risk": 1,
    "has_white_method": 0,
    "hidden_owner": "0",
    "holder_analysis": {
      "average_tax": 0,
      "balance_disappeared": 0,
      "sell_failure": 0,
      "sell_successful": 408,
      "simulate_holders": 408,
      "tax_distribution": [
        {
          "count": 408,
          "tax": 0
        }
      ]
    },
    "holders": 47915,
    "honeypot_with_same_creator": "0",
    "is_anti_whale": "0",
    "is_honeypot": -1,
    "is_in_dex": "1",
    "is_proxy": "0",
    "lock_amount": 0,
    "owner": "0x0000000000000000000000000000000000000000",
    "owner_balance": "0",
    "owner_change_balance": "0",
    "owner_percent": "0.000000",
    "pair_holders": 3,
    "pair_holders_rank": [
      {
        "address": "0x000000000000000000000000000000000000dead",
        "lock": [],
        "mark": "Blackhole/????",
        "percent": "0.9959615547609384",
        "quantity": "316227.7660168379"
      },
      {
        "address": "0x0ed943ce24baebf257488771759f9bf482c39706",
        "is_contract": 1,
        "mark": null,
        "percent": "0.0040384452390615",
        "quantity": "1282.2467996129594"
      },
      {
        "address": "0x0000000000000000000000000000000000000000",
        "lock": [],
        "mark": "Blackhole/????",
        "percent": "0.000000",
        "quantity": "0.000000000000001"
      }
    ],
    "pair_lock_percent": 0.9959615547609385,
    "pair_total": 317510.01281645085,
    "personal_slippage_modifiable": "0",
    "previous_owner": "0xb779A009E99512cA46Bc76a4Df26E6DD58EE22eA",
    "query_count": 99999,
    "risk_score": 40,
    "selfdestruct": "0",
    "sell_gas": "0.00370724838219348933493",
    "sell_tax": 0,
    "slippage_modifiable": 0,
    "token": "0x92aa03137385f18539301349dcfc9ebc923ffb10",
    "token_holders_rank": [
      {
        "address": "0x73d8bd54f7cf5fab43fe4ef40a62d390644946db",
        "is_contract": 1,
        "mark": null,
        "percent": "0.0616787537777854",
        "quantity": "61678753.77778536"
      },
      {
        "address": "0xbc42145d5a574ede9b8860fca2a49eb7b239efa5",
        "is_contract": 1,
        "is_lp": 1,
        "mark": "Cakev2: SKYAI/WBNB",
        "percent": "0.042684021957507",
        "quantity": "42684021.957506984"
      },
      {
        "address": "0x0d0707963952f2fba59dd06f2b425ace40b492fe",
        "is_contract": null,
        "mark": "Gate.io",
        "percent": "0.0230227049009298",
        "quantity": "23022704.90092981"
      },
      {
        "address": "0x69b86059c5fb3a44355937e7b505a659443b9a22",
        "is_contract": 1,
        "is_lp": 1,
        "mark": "Pancakev3: SKYAI/USDT",
        "percent": "0.0169822779919881",
        "quantity": "16982277.991988137"
      },
      {
        "address": "0x65db427d94760cfaa14aa1028c5e398193bec302",
        "is_contract": null,
        "mark": null,
        "percent": "0.0133556794415548",
        "quantity": "13355679.44155482"
      },
      {
        "address": "0x24b9aa9a77e2d61b7802890d78abdac978a22286",
        "is_contract": null,
        "mark": null,
        "percent": "0.0089946734497009",
        "quantity": "8994673.449700907"
      },
      {
        "address": "0xa27419dd34017daf3d48c8591363aea28d7c9a84",
        "is_contract": null,
        "mark": null,
        "percent": "0.0054761290904647",
        "quantity": "5476129.090464694"
      },
      {
        "address": "0x48d6f114628a8b61eb7a5add0b80148292c3f9ea",
        "is_contract": null,
        "mark": null,
        "percent": "0.005",
        "quantity": "5000000"
      },
      {
        "address": "0xf972e08cf74af7178b2a27ffd8809b206652bb9b",
        "is_contract": null,
        "mark": null,
        "percent": "0.0048431389318884",
        "quantity": "4843138.931888364"
      },
      {
        "address": "0x4e1a6bec38106a99ffda1378e483727b8816de40",
        "is_contract": null,
        "mark": null,
        "percent": "0.0040967838998149",
        "quantity": "4096783.899814857"
      }
    ],
    "token_lock_percent": 0,
    "token_name": "SKYAI",
    "token_symbol": "SKYAI",
    "total": "1000000000",
    "trading_cooldown": "0",
    "transfer_pausable": "0",
    "transfer_tax": "0",
    "version": "v1.3.0",
    "vote_support": "2"
  }
}
```
````

{% endtab %}
{% endtabs %}

