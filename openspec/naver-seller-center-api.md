# Naver Smart Store Seller Center - Discovered API Endpoints

Base URL: `https://sell.smartstore.naver.com`

The seller center is an AngularJS SPA (`ng-app="center"`). API calls are made from `app.js` using
`$resource` factories. Authentication flows through Naver NID cookies + a server-side `kit.session`
cookie. Channel selection requires POST `/api/login/change-channel`.

## Architecture

- **Main SPA**: `https://sell.smartstore.naver.com/` (hash-based routing: `/#/home/dashboard`)
- **JS Bundles**: `app.js` (6.6MB), `vendors.js` (9.1MB)
- **Order Management (v3)**: Separate SPA at `/o/v3/...` with its own JS bundles
- **API Gateway**: Two distinct backends:
  - Legacy: returns `{"code":"BAD_REQUEST","message":"..."}` (direct Spring backend)
  - GW: returns `{"code":"GW.AUTHN","message":"...","traceId":"..."}` (API gateway)

## Authentication Flow

1. **Login**: Browser-based Naver ID login at `accounts.commerce.naver.com`
2. **Session Cookies**: `NID_SES`, `NID_AUT`, `NSI`, `kit.session`, `CBI_SES`, `CBI_CHK`
3. **Channel Selection**: `POST /api/login/change-channel?roleNo={roleNo}&channelNo={channelNo}&url=/`
4. **Session Init**: `GET /api/login/init?stateName={stateName}&needLoginInfoForAngular=true`
5. **Interceptor Headers**:
   - `X-NCP-LOGIN-INFO` — login state info
   - `X-Ses-Valid` — session validity flag (returned in response headers)
   - `x-current-state` / `x-current-stateName` / `x-to-stateName` — SPA state tracking

## Confirmed Working Endpoints (HTTP 200)

### No Authentication Required (Public/Static)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/product/delivery/companies` | GET | List of all delivery companies (택배사) |

### Session Authentication Required
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/context` | GET | App bootstrap context (menus, locale, device) | 205KB JSON |
| `/api/login/channels` | GET | Available channels for logged-in user | Channel list with channelNo, accountNo, etc. |
| `/api/login/roles` | GET | User roles | Array |
| `/api/login/check-neoid-session` | GET | Check NeoID session | `{"existNeoIdSession": true}` |
| `/api/seller/notification` | GET | Seller notifications | Object |
| `/api/member/nchat/connect?channelNo={channelNo}` | GET | NChat connection info | Server URL, userInfo, channelNames |
| `/api/v3/contents/reviews/dash-board/review-count` | GET | Review count dashboard | scoreCountMap, reviewContentTypeCountMap |
| `/api/v3/contents/reviews/dash-board/low-score` | GET | Low score reviews | Array |
| `/api/v2/product-enums/codes?enumNames={names}` | GET | Product enum codes | Enum definitions |
| `/api/v2/data-statistics/search-inflow/channel-products` | GET | Search inflow stats | 204 (no data) |

## Endpoints Requiring Channel + _action Parameter (Authenticated)

These endpoints return `GW.AUTHN` 403 when session is invalid, and `BAD_REQUEST` 400 when
session is valid but `_action` parameter is missing.

### Products
| Endpoint | Method | _action | Description |
|----------|--------|---------|-------------|
| `/api/products/list` | **POST** | `search` → `/api/products/list/search` | Search products |
| `/api/products/list` | GET | — | Product list (base resource) |
| `/api/channel-products/list` | GET | — | Channel product list |
| `/api/channel-products/list/search` | **POST** | — | Channel product search |
| `/api/channel-products/search-exposure-infos` | GET | — | Exposure info |
| `/api/channel-products/search-popular` | GET | — | Popular products |

### Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboards/pay/sale-stats` | GET | Sales statistics |
| `/api/dashboards/pay/order-delivery` | GET | Order delivery info |
| `/api/dashboards/pay/claim` | GET | Claim info |
| `/api/dashboards/pay/purchase-completion` | GET | Purchase completion info |
| `/api/dashboards/pay/sales-delay` | GET | Sales delay info |
| `/api/dashboards/pay/settlement` | GET | Settlement dashboard info |
| `/api/dashboards/channel/products` | GET | Channel products summary |
| `/api/dashboards/account/penalties` | GET | Penalty info |
| `/api/dashboards/seller-grade` | GET | Seller grade |
| `/api/dashboards/best-price-products` | GET | Best price products |
| `/api/dashboards/banners` | GET | Banners (isArray) |
| `/api/dashboards/talktalk-reception-status` | GET | TalkTalk reception status |
| `/api/dashboards/naver-shopping-search-trend` | GET | Shopping search trend |
| `/api/dashboards/channel/sale-performance` | GET | Sale performance |
| `/api/dashboards/best-keyword` | GET | Best keyword |
| `/api/dashboards/modals` | GET | Dashboard modals |

### Sales & Statistics
| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/sales-day/with-from-to` | GET | `fromDateString`, `toDateString` | Daily sales in range |
| `/api/sale-summaries` | GET | `_action=queryPage` | Sale summaries (paged) |
| `/api/sale-summaries/downloadExcel` | POST | — | Excel download |

### Settlements
| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/settlements` | GET | `_action=queryPage` | Settlement list (paged) |
| `/api/settlements/downloadExcel` | POST | — | Excel download |

### Reviews
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v3/contents/reviews/search` | GET/POST | Search reviews |
| `/api/v3/contents/reviews/comment` | GET | Review comments |
| `/api/v3/contents/reviews/comment/bulk-create` | POST | Bulk create comments |
| `/api/v3/contents/reviews/download-excel` | POST | Excel download |
| `/api/v3/contents/reviews/movement/search` | GET | Review movement |
| `/api/v3/contents/reviews/sync` | GET | Sync reviews |
| `/api/v3/contents/reviews/sync/product-review-statistic` | GET | Product review stats |

### Seller Info
| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/seller/info` | GET | `ssnShow=true` (optional) | Seller info |
| `/api/seller/info?chrgrChangeShow=true` | GET | — | Seller info with charge change |
| `/api/seller/info/modHistory` | GET | `id`, `sellerInfoModHistorySearchType` | Modification history |
| `/api/sellers/account` | GET | `mask`, `maskApplyTypes` | Account info |
| `/api/sellers/bank-account` | GET | — | Bank account |
| `/api/sellers/escrow/print` | GET | — | Escrow document print |
| `/api/v1/sellers` | GET | — | Seller info v1 |

### Channels
| Endpoint | Method | _action | Description |
|----------|--------|---------|-------------|
| `/api/channels/:id` | GET | `mask` | Channel info |
| `/api/channels` | GET | `selectedChannel` | Currently selected channel |
| `/api/channels` | GET | `managedChannelList` | Managed channel list |
| `/api/channels` | GET | `groupManagerChannelList` | Group manager channels |

### Categories
| Endpoint | Method | _action | Description |
|----------|--------|---------|-------------|
| `/api/categories` | GET | (none) | Category list (isArray) |
| `/api/categories` | GET | `queryPage` | Category list (paged) |
| `/api/categories/:id` | GET | — | Single category |
| `/api/categories/:id` | GET | `getWithRestrictCategory` | With restriction info |

### MyConfigs (Store Configuration)
| Endpoint | Method | _action | Description |
|----------|--------|---------|-------------|
| `/api/myconfigs` | GET | `getChannels` | Channels under account |
| `/api/myconfigs` | GET | `getJoinApplyChannels` | Join apply channels |
| `/api/myconfigs/exposure` | GET | — | Exposure settings |
| `/api/myconfigs/price` | GET | — | Price settings |
| `/api/myconfigs/toolkit` | GET | — | Toolkit settings |

### Credit & Penalty
| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/credit/history` | GET | `_action=init`, `startDate`, `endDate` | Credit score history |
| `/api/penalty` | GET | `_action=getProhibitProductRegistAccounts` | Penalty info |

### Delivery
| Endpoint | Method | _action | Description |
|----------|--------|---------|-------------|
| `/api/delivery-bundle-groups` | GET | `queryPage` | Delivery bundle groups |
| `/api/delivery-bundle-groups` | GET | `base` with `accountNo` | Base config |
| `/api/delivery-bundle-groups/:id` | GET | — | Single group |
| `/api/product/delivery/companies` | GET | — | All delivery companies |

### TalkTalk / Chat
| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/shared/talktalk` | GET | `_action=isTalkExposure&channelNo={channelNo}` | TalkTalk exposure check |
| `/api/myconfigs/toolkit/talktalk` | GET | `_action=getToken` | TalkTalk token |
| `/api/myconfigs/toolkit/talktalk` | GET | `_action=isTalkExposure&channelNo={channelNo}` | TalkTalk exposure |

### Enum/Code Endpoints
| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/v1/sellers/shared/codes` | GET | `enumNames=...` | Seller enum codes |
| `/api/v2/product-enums/codes` | GET | `enumNames=...` | Product enum codes |
| `/api/v3/contents-enums/codes` | GET | `enumNames=...` | Content enum codes |
| `/api/v2/benefit/enums` | GET | `enumNames=...` | Benefit enum codes |
| `/api/v1/benefit/enums/codes` | GET | `enumNames=...` | Benefit v1 enum codes |
| `/api/v2/marketing/enums` | GET | `enumNames=...` | Marketing enum codes |
| `/api/v2/coin/enums` | GET | — | Coin enums |

## Login / Session Management
| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/login/channels` | GET | — | Available channels |
| `/api/login/roles` | GET | — | User roles |
| `/api/login/init` | GET | `stateName`, `needLoginInfoForAngular` | Initialize login session |
| `/api/login/change-channel` | **POST** | `roleNo`, `channelNo`, `url` | Select active channel |
| `/api/login/changeChannelByToken` | **POST** | `token`, `url` | Change channel by token |
| `/api/login/check-neoid-session` | GET | — | Check NeoID session |

## Order Management (v3 SPA)

The order management uses a separate SPA under `/o/v3/`:

| Endpoint | Description |
|----------|-------------|
| `/o/v3/order/summary` | Order summary page (HTML) |
| `/o/v3/manage/order` | Order management (HTML) |
| `/o/v3/n/sale/delivery` | Delivery management (HTML) |
| `/o/v3/n/sale/delivery/situation` | Delivery situation (HTML) |
| `/o/v3/sale/unpayment` | Unpaid orders (HTML) |
| `/o/v3/sale/purchaseDecision/list` | Purchase decision list (HTML) |
| `/o/v3/claim/cancel` | Cancel claims (HTML) |
| `/o/v3/claim/exchange` | Exchange claims (HTML) |
| `/o/v3/claim/return` | Return claims (HTML) |
| `/o/v3/claim/returnCare/management` | Return care management (HTML) |

The v3 SPA uses its own JS bundles (`common.bundle.js`, `order.bundle.js`) and a separate
API at `/api/meta/enums`.

## Data Statistics (v2)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/data-statistics` | GET | Data statistics |
| `/api/v2/data-statistics/search-inflow/channel-products` | GET | Search inflow for products |

## Key Channel Info (from `/api/login/channels` response)
```json
{
  "channelNo": 1100114368,
  "accountNo": 1100112229,
  "representNo": 1100110443,
  "type": "STOREFARM",
  "channelName": "hellodev",
  "storeExhibitionType": "SMART_STORE",
  "url": "https://smartstore.naver.com/hellodev",
  "accountId": "ncp_i6z811_01",
  "defaultChannelNo": 1100114368,
  "accountStatusType": "NORMAL",
  "roleNo": 200206319,
  "roleGroupType": "REPRESENT",
  "actionGrade": "FIFTH"
}
```

## Notes

1. **POST-only endpoints**: `products/list/search`, `channel-products/list/search`,
   `login/change-channel`, `login/changeChannelByToken`, `bizadvisor/createToken` all
   require POST. GET returns 405.

2. **_action parameter**: Many endpoints use `_action` query parameter to distinguish
   between different operations on the same resource URL (AngularJS `$resource` pattern).

3. **Session lifecycle**: The session requires:
   - Valid NID cookies (from Naver login)
   - `kit.session` cookie (commerce platform session)
   - Channel selection via `POST /api/login/change-channel`
   - Then `GET /api/login/init` to initialize the SPA state

4. **Two API gateways**: Endpoints are routed through different backends:
   - Legacy backend (`sell.smartstore.naver.com` direct): returns standard error codes
   - API Gateway: returns `GW.*` error codes with `traceId`

5. **Settlements backend**: Consistently returns HTTP 502, suggesting a separate
   microservice that may be down or require different routing.

6. **Products are POST-based**: `products/list` and `channel-products/list` use POST
   for search/list operations (with request body for search criteria), not GET.
