# Naver Smart Store API Response Log

Generated: 2026-03-26T01:27:38.005442

---

## Login Channels

- **Endpoint:** `GET /api/login/channels`
- **Status:** `200`

**Response:**

```json
[
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
    "accountExternalStatusType": "NORMAL",
    "advertiser": true,
    "representType": "DOMESTIC_PERSONAL",
    "roleNo": 200206319,
    "roleGroupType": "REPRESENT",
    "roleRangeNo": 1100110443,
    "actionGrade": "FIFTH",
    "serviceSatisfactionGrade": false,
    "loginableAccountSelectVOs": [],
    "showOption": false
  }
]
```

---

## Change Channel

- **Endpoint:** `POST /api/login/change-channel?roleNo=200206319&channelNo=1100114368&url=/`
- **Status:** `200`

**Response:**

```json
(empty)
```

---

## Login Init

- **Endpoint:** `GET /api/login/init?stateName=home.dashboard&needLoginInfoForAngular=true`
- **Status:** `200`

**Response:**

```json
(empty)
```

---

## Dashboard Sale Stats

- **Endpoint:** `GET /api/dashboards/pay/sale-stats`
- **Status:** `200`

**Response:**

```json
{
  "paymentWaitCases": "0",
  "newOrderCases": "0",
  "todayDispatchCases": "0",
  "preOrderCases": "0",
  "subscriptionCases": "0",
  "deliveryPreparingCases": "0",
  "deliveringCases": "0",
  "deliveredCases": "0",
  "arrivalGuaranteeCases": "0",
  "unacceptedGiftCases": "0"
}
```

---

## Dashboard Order Delivery

- **Endpoint:** `GET /api/dashboards/pay/order-delivery`
- **Status:** `200`

**Response:**

```json
{
  "paymentWaitCases": 0,
  "newOrderCases": 0,
  "todayDispatchCases": 0,
  "preOrderCases": 0,
  "subscriptionCases": 0,
  "deliveryPreparingCases": 0,
  "deliveringCases": 0,
  "deliveredCases": 0,
  "arrivalGuaranteeCases": 0,
  "unacceptedGiftCases": 0,
  "purchaseCompletionCases": 0
}
```

---

## Dashboard Channel Products

- **Endpoint:** `GET /api/dashboards/channel/products`
- **Status:** `200`

**Response:**

```json
{
  "onSaleProductCount": "0",
  "onOutOfStockProductCount": "0",
  "modifyRequestProductCount": "0"
}
```

---

## Dashboard Settlement

- **Endpoint:** `GET /api/dashboards/pay/settlement`
- **Status:** `200`

**Response:**

```json
{
  "todayAmount": "0",
  "quickTodayAmount": "0",
  "expectedAmount": "0",
  "quickExpectedAmount": "0",
  "chargeBalance": "0",
  "hasQuickSettleApplicationHistory": false,
  "isQuickSettleNeverApplied": true,
  "isQuickSettleAppliable": false,
  "nextWorkingDay": "20260327"
}
```

---

## Review Count

- **Endpoint:** `GET /api/v3/contents/reviews/dash-board/review-count`
- **Status:** `200`

**Response:**

```json
{
  "scoreCountMap": {},
  "reviewContentTypeCountMap": {},
  "eventProgressStatusCountMap": {}
}
```

---

## Channel Product List Search

- **Endpoint:** `POST /api/channel-products/list/search`
- **Status:** `400`
- **Request Body:** `{"searchOrderType": "RECENTLY_REGISTERED", "searchKeywordType": "ALL", "page": 1, "pageSize": 10, "searchChannelProductDisplayStatusTypes": []}`

**Response:**

```json
{
  "code": "BAD_REQUEST",
  "message": "입력한 데이터가 유효하지 않습니다.",
  "invalidInputs": [
    {
      "name": "searchOrderType",
      "type": "NotEmpty",
      "message": "정렬조건 항목을 입력해 주세요."
    }
  ],
  "timestamp": "2026-03-25T16:27:35.971+00:00",
  "needAlert": true
}
```

---

## Daily Sales (legacy)

- **Endpoint:** `GET /api/sales-day/with-from-to?fromDateString=20260301&toDateString=20260326`
- **Status:** `400`

**Response:**

```json
{
  "code": "BAD_REQUEST",
  "message": "입력정보가 올바르지 않습니다.",
  "timestamp": "2026-03-25T16:27:36.054+0000",
  "needAlert": true
}
```

---

## Seller Info (legacy)

- **Endpoint:** `GET /api/seller/info`
- **Status:** `400`

**Response:**

```json
{
  "code": "BAD_REQUEST",
  "message": "입력정보가 올바르지 않습니다.",
  "timestamp": "2026-03-25T16:27:36.100+0000",
  "needAlert": true
}
```

---

## Sales Summary Full Chart (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/account/sales-summary-full-chart?isRefresh=true`
- **Status:** `200`

**Response:**

```json
{
  "baseDate": "2026-03-24",
  "accountId": "ncp_i6z811_01",
  "pvCount": {
    "daily": 0,
    "dailyPrev": 0,
    "dailyChartData": {
      "desc": "일간 방문수 차트 데이터",
      "items": []
    },
    "weekly": 0,
    "weeklyPrev": 0,
    "weeklyChartData": {
      "desc": "주간 방문수 차트 데이터",
      "items": []
    },
    "monthly": 0,
    "monthlyPrev": 0,
    "monthlyChartData": {
      "desc": "월간 방문수 차트 데이터",
      "items": []
    }
  },
  "orderCount": {
    "daily": 0,
    "dailyPrev": 0,
    "dailyChartData": {
      "desc": "일간 상품주문건수 차트 데이터",
      "items": []
    },
    "weekly": 0,
    "weeklyPrev": 0,
    "weeklyChartData": {
      "desc": "주간 상품주문건수 차트 데이터",
      "items": []
    },
    "monthly": 0,
    "monthlyPrev": 0,
    "monthlyChartData": {
      "desc": "월간 상품주문건수 차트 데이터",
      "items": []
    }
  },
  "orderConversionRate": {
    "daily": 0,
    "dailyPrev": 0,
    "dailyChartData": {
      "desc": "일간 구매전환율 차트 데이터",
      "items": []
    },
    "weekly": 0,
    "weeklyPrev": 0,
    "weeklyChartData": {
      "desc": "주간 구매전환율 차트 데이터",
      "items": []
    },
    "monthly": 0,
    "monthlyPrev": 0,
    "monthlyChartData": {
      "desc": "월간 구매전환율 차트 데이터",
      "items": []
    }
  },
  "orderAverageAmount": {
    "daily": 0,
    "dailyPrev": 0,
    "dailyChartData": {
      "desc": "일간 상품주문단가 차트 데이터",
      "items": []
    },
    "weekly": 0,
    "weeklyPrev": 0,
    "weeklyChartData": {
      "desc": "주간 상품주문단가 차트 데이터",
      "items": []
    },
    "monthly": 0,
    "monthlyPrev": 0,
    "monthlyChartData": {
      "desc": "월간 상품주문단가 차트 데이터",
      "items": []
    }
  },
  "payAmount": {
    "daily": 0,
    "dailyPrev": 0,
    "dailyChartData": {
      "desc": "일간 결제금액 차트 데이터",
      "items": []
    },
    "weekly": 0,
    "weeklyPrev": 0,
    "weeklyChartData": {
      "desc": "주간 결제금액 차트 데이터",
      "items": []
    },
    "monthly": 0,
    "monthlyPrev": 0,
    "monthlyChartData": {
      "desc": "월간 결제금액 차트 데이터",
      "items": []
    }
  }
}
```

---

## Order Delivery (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/pay/order-delivery`
- **Status:** `200`

**Response:**

```json
{
  "paymentWaitCases": 0,
  "newOrderCases": 0,
  "todayDispatchCases": 0,
  "preOrderCases": 0,
  "subscriptionCases": 0,
  "deliveryPreparingCases": 0,
  "deliveringCases": 0,
  "deliveredCases": 0,
  "arrivalGuaranteeCases": 0,
  "unacceptedGiftCases": 0,
  "purchaseCompletionCases": 0
}
```

---

## Settlement (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/pay/settlement`
- **Status:** `200`

**Response:**

```json
{
  "todayAmount": "0",
  "quickTodayAmount": "0",
  "expectedAmount": "0",
  "quickExpectedAmount": "0",
  "chargeBalance": "0",
  "hasQuickSettleApplicationHistory": false,
  "isQuickSettleNeverApplied": true,
  "isQuickSettleAppliable": false,
  "nextWorkingDay": "20260327"
}
```

---

## Channel Products (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/channel/products`
- **Status:** `200`

**Response:**

```json
{
  "onSaleProductCount": "0",
  "onOutOfStockProductCount": "0",
  "modifyRequestProductCount": "0"
}
```

---

## Dashboard Reviews (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/reviews`
- **Status:** `200`

**Response:**

```json
{
  "scoreCountMap": {},
  "eventProgressStatusCountMap": {}
}
```

---

## Dashboard Inquiries (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/inquiries`
- **Status:** `200`

**Response:**

```json
{
  "productInquiryCount": "0",
  "customerInquiryCount": "0",
  "talktalkInquiryCount": "0",
  "productInquiries": [],
  "customerInquiries": []
}
```

---

## Seller Grade (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/seller-grade`
- **Status:** `200`

**Response:**

```json
{
  "actionGrade": "FIFTH",
  "goodServiceYn": false,
  "appliedYM": "000000"
}
```

---

## Store Customer Status (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/channel/store-customer-status?channelNo=1100114368&withChannelInfo=true`
- **Status:** `200`

**Response:**

```json
{
  "baseDate": "2026-03-24T08:17:37.010+0000",
  "storeVisitorStatistics": {
    "visitorHours": [
      "0",
      "1",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "19",
      "20",
      "21",
      "22",
      "23"
    ],
    "visitorCounts": [
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0
    ],
    "totalVisitorCount": 0
  },
  "channelNewsCustomerStatistics": {
    "total": 0,
    "female": 0,
    "male": 0,
    "a10s": 0,
    "a20s": 0,
    "a30s": 0,
    "a40s": 0,
    "a50s": 0,
    "maxAge": 0,
    "minAge": 0
  },
  "channelInfoList": [
    {
      "channelNo": "1100114368",
      "channelName": "hellodev",
      "channelRepresentImageUrl": "",
      "channelStoreEndPcUrl": "https://smartstore.naver.com/hellodev",
      "channelStoreEndMobileUrl": "https://m.smartstore.naver.com/hellodev",
      "channelLabelInfo": {
        "type": "STOREFARM"
      }
    }
  ]
}
```

---

## Dashboard Claims (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/pay/claim`
- **Status:** `200`

**Response:**

```json
{
  "cancelClaimCases": "0",
  "returnClaimCases": "0",
  "returnCollectDoneCases": "0",
  "exchangeClaimCases": "0",
  "exchangeCollectDoneCases": "0"
}
```

---

## Good Service Score (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/good-service-score`
- **Status:** `200`

**Response:**

```json
{
  "targetDate": "20260325"
}
```

---

## Account Penalties (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/account/penalties`
- **Status:** `200`

**Response:**

```json
{
  "occurredScoreTotal": 0,
  "occurredScoreRatio": 0,
  "restraintStepString": "-",
  "restraintStep": "NO",
  "appliedYmd": "2026-03-24T17:39:55.000+0000"
}
```

---

## Group Product Info (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/group-product-info`
- **Status:** `200`

**Response:**

```json
{
  "groupProductAvailableCount": 0
}
```

---

## Ranking Diagnosis (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/ranking-diagnosis`
- **Status:** `200`

**Response:**

```json
{
  "hideCard": true
}
```

---

## Product Diagnosis (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/product-diagnosis`
- **Status:** `200`

**Response:**

```json
{
  "hideCard": true
}
```

---

## Onboarding (v1)

- **Endpoint:** `GET /api/v1/sellers/dashboards/onboarding`
- **Status:** `200`

**Response:**

```json
{
  "memberNo": 1100280132,
  "accountNo": 1100112229,
  "completed": false
}
```

---

## Seller Context / Menu (v1)

- **Endpoint:** `GET /api/v1/sellers/context/for-resource-menu`
- **Status:** `200`

**Response:**

```json
{
  "mobile": false,
  "mobileAgent": false,
  "tablet": false,
  "na": false,
  "sellerApp": false,
  "device": "UNKNOWN",
  "locale": "en_US",
  "country": "US",
  "menus": [
    {
      "id": {
        "id": 110000000002,
        "regTime": 1759111721000
      },
      "state": " ",
      "name": "상품관리",
      "type": "LNB",
      "icon": "product",
      "ownTitleBar": false,
      "onlyDev": false,
      "isBetaMenu": false,
      "isNewMenu": false,
      "depth": 1,
      "children": [
        {
          "id": {
            "id": 113412619,
            "regTime": 1759111721000
          },
          "state": " ",
          "name": "상품 조회/수정",
          "type": "LNB",
          "ownTitleBar": false,
          "onlyDev": false,
          "isBetaMenu": false,
          "isNewMenu": false,
          "depth": 2,
          "parentState": " ",
          "children": [],
          "acl": {
            "noLogin": false,
            "skipStatus": false,
            "onlySupplyAccount": false,
            "hasSupplyAccount": true,
            "accessibleOwnChannelType": [
              "STOREFARM",
              "WINDOW"
            ],
            "accessibleAccountStatus": [
              "STOP",
              "LEAVE_APPLY",
              "JOIN_APPLY"
            ],
            "accessibleRoleDetail": [
              "INFLUENCER",
              "AGENCY"
            ],
            "onlyNaverpay": false,
            "onlyAdvertiser": false,
            "isBenefitMenu": false,
            "isBranchMenu": true,
            "denyQuickCommerce": false,
            "accessDenyKeys": [
              "BRAND_STORE_CATALOG"
            ]
          },
          "isShowPopupNoticeMenu": false,
          "parentMenuNo": 110000000002,
          "menuType": "BASIC",
          "phase": "r-real",
          "version": "v0",
          "menuResource": {
            "resourceIdentity": "/products/origin-list",
            "resourceType": "PATH"
          }
        }
      ],
      "acl": {

... (truncated)
```

---

