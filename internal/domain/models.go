package domain

// OrderDeliveryDashboard maps the response from
// GET /api/v1/sellers/dashboards/pay/order-delivery
type OrderDeliveryDashboard struct {
	PaymentWaitCases        int `json:"paymentWaitCases"`
	NewOrderCases           int `json:"newOrderCases"`
	TodayDispatchCases      int `json:"todayDispatchCases"`
	PreOrderCases           int `json:"preOrderCases"`
	SubscriptionCases       int `json:"subscriptionCases"`
	DeliveryPreparingCases  int `json:"deliveryPreparingCases"`
	DeliveringCases         int `json:"deliveringCases"`
	DeliveredCases          int `json:"deliveredCases"`
	ArrivalGuaranteeCases   int `json:"arrivalGuaranteeCases"`
	UnacceptedGiftCases     int `json:"unacceptedGiftCases"`
	PurchaseCompletionCases int `json:"purchaseCompletionCases"`
}

// ProductDashboard maps the response from
// GET /api/v1/sellers/dashboards/channel/products
type ProductDashboard struct {
	OnSaleProductCount        string `json:"onSaleProductCount"`
	OnOutOfStockProductCount  string `json:"onOutOfStockProductCount"`
	ModifyRequestProductCount string `json:"modifyRequestProductCount"`
}

// ProductSearchResponse maps the response from
// POST /api/products/list/search
type ProductSearchResponse struct {
	Content  []ProductSearchItem `json:"content"`
	Total    int                 `json:"total"`
	Pageable struct {
		Page int `json:"page"`
		Size int `json:"size"`
	} `json:"pageable"`
}

// ProductSearchItem represents a single product from the search response.
type ProductSearchItem struct {
	ChannelProductNo     int64  `json:"channelProductNo"`
	ProductName          string `json:"name"`
	SalePrice            int64  `json:"salePrice"`
	StockQuantity        int    `json:"stockQuantity"`
	ChannelProductStatus string `json:"statusType"`
	CategoryName         string `json:"wholeCategoryName"`
	RegDate              string `json:"regDate"`
	ModDate              string `json:"modDate"`
}

// SettlementDashboard maps the response from
// GET /api/v1/sellers/dashboards/pay/settlement
type SettlementDashboard struct {
	TodayAmount                      string `json:"todayAmount"`
	QuickTodayAmount                 string `json:"quickTodayAmount"`
	ExpectedAmount                   string `json:"expectedAmount"`
	QuickExpectedAmount              string `json:"quickExpectedAmount"`
	ChargeBalance                    string `json:"chargeBalance"`
	HasQuickSettleApplicationHistory bool   `json:"hasQuickSettleApplicationHistory"`
	IsQuickSettleNeverApplied        bool   `json:"isQuickSettleNeverApplied"`
	IsQuickSettleAppliable           bool   `json:"isQuickSettleAppliable"`
	NextWorkingDay                   string `json:"nextWorkingDay"`
}

// SalesSummary maps the response from
// GET /api/v1/sellers/dashboards/account/sales-summary-full-chart?isRefresh=true
type SalesSummary struct {
	BaseDate   string      `json:"baseDate"`
	AccountID  string      `json:"accountId"`
	PVCount    SalesMetric `json:"pvCount"`
	OrderCount SalesMetric `json:"orderCount"`
	PayAmount  SalesMetric `json:"payAmount"`
}

// SalesMetric holds daily/weekly/monthly counts for a given metric.
type SalesMetric struct {
	Daily       int `json:"daily"`
	DailyPrev   int `json:"dailyPrev"`
	Weekly      int `json:"weekly"`
	WeeklyPrev  int `json:"weeklyPrev"`
	Monthly     int `json:"monthly"`
	MonthlyPrev int `json:"monthlyPrev"`
}

// InquiryDashboard maps the response from
// GET /api/v1/sellers/dashboards/inquiries
type InquiryDashboard struct {
	ProductInquiryCount  string        `json:"productInquiryCount"`
	CustomerInquiryCount string        `json:"customerInquiryCount"`
	TalktalkInquiryCount string        `json:"talktalkInquiryCount"`
	ProductInquiries     []InquiryItem `json:"productInquiries"`
	CustomerInquiries    []InquiryItem `json:"customerInquiries"`
}

// InquiryItem represents a single inquiry in the dashboard response.
type InquiryItem struct {
	Title     string `json:"title"`
	CreatedAt string `json:"createdDate"`
}

// ReviewDashboard maps the response from
// GET /api/v1/sellers/dashboards/reviews
type ReviewDashboard struct {
	ReviewCount         int     `json:"reviewCount"`
	ReviewAvgScore      float64 `json:"reviewAvgScore"`
	ManagerCommentCount int     `json:"managerCommentCount"`
}

// ReviewSearchResponse maps the response from
// POST /api/v3/contents/reviews/search
type ReviewSearchResponse struct {
	Contents      []ReviewItem `json:"contents"`
	Page          int          `json:"page"`
	Size          int          `json:"size"`
	TotalElements int          `json:"totalElements"`
	TotalPages    int          `json:"totalPages"`
	First         bool         `json:"first"`
	Last          bool         `json:"last"`
}

// ReviewItem represents a single review from the search response.
type ReviewItem struct {
	ReviewID    string `json:"id"`
	ProductName string `json:"productName"`
	Score       int    `json:"score"`
	Content     string `json:"content"`
	BuyerID     string `json:"buyerId"`
	CreatedDate string `json:"createDate"`
}

// SellerGrade maps the response from
// GET /api/v1/sellers/dashboards/seller-grade
type SellerGrade struct {
	ActionGrade   string `json:"actionGrade"`
	GoodServiceYN bool   `json:"goodServiceYn"`
	AppliedYM     string `json:"appliedYM"`
}

// Penalties maps the response from
// GET /api/v1/sellers/dashboards/account/penalties
type Penalties struct {
	OccurredScoreTotal  int     `json:"occurredScoreTotal"`
	OccurredScoreRatio  float64 `json:"occurredScoreRatio"`
	RestraintStepString string  `json:"restraintStepString"`
	RestraintStep       string  `json:"restraintStep"`
	AppliedYmd          string  `json:"appliedYmd"`
}

// LoginChannel represents a channel returned from GET /api/login/channels.
type LoginChannel struct {
	ChannelNo   int64  `json:"channelNo"`
	RoleNo      int64  `json:"roleNo"`
	ChannelName string `json:"channelName"`
	AccountNo   int64  `json:"accountNo"`
}

// SellerInfo maps the response from GET /api/channels?_action=selectedChannel.
type SellerInfo struct {
	ChannelID     int64  `json:"id"`
	ChannelName   string `json:"name"`
	ChannelURL    string `json:"url"`
	FullURL       string `json:"fullUrl"`
	ChannelType   string `json:"type"`
	ChannelStatus string `json:"channelStatusType"`
	SellerStatus  string `json:"sellerStatusType"`
	Account       struct {
		ID        int64  `json:"id"`
		AccountID string `json:"accountId"`
	} `json:"account"`
	Represent struct {
		RepresentName string `json:"representName"`
		RepresentType string `json:"representType"`
	} `json:"represent"`
	Pay struct {
		ID            int64  `json:"id"`
		BankCode      string `json:"bankCode"`
		BankName      string `json:"bankName"`
		AccountHolder string `json:"accountHolder"`
	} `json:"pay"`
	ContactInfo struct {
		TelNo struct {
			FormattedNumber string `json:"formattedNumber"`
		} `json:"telNo"`
	} `json:"contactInfo"`
}

// NotificationCounts maps category names to unread counts.
type NotificationCounts map[string]int

// OrderListResponse is the GraphQL response for order status query.
type OrderListResponse struct {
	Data struct {
		OrderStatus OrderStatusResult `json:"orderStatus_ForOrderStatus"`
	} `json:"data"`
}

// OrderStatusResult holds the elements and pagination from the order status query.
type OrderStatusResult struct {
	Elements   []OrderItem     `json:"elements"`
	Pagination OrderPagination `json:"pagination"`
}

// OrderItem represents a single order from the GraphQL response.
type OrderItem struct {
	ProductOrderNo     string `json:"productOrderNo"`
	OrderNo            string `json:"orderNo"`
	OrderDateTime      string `json:"orderDateTime"`
	ProductOrderStatus string `json:"productOrderStatus"`
	ProductName        string `json:"productName"`
	OrderQuantity      int    `json:"orderQuantity"`
	OrderMemberName    string `json:"orderMemberName"`
	ReceiverName       string `json:"receiverName"`
	ClaimStatus        string `json:"claimStatus"`
}

// OrderPagination holds pagination info from the GraphQL order status response.
type OrderPagination struct {
	Size          int    `json:"size"`
	TotalElements string `json:"totalElements"`
	Page          int    `json:"page"`
	TotalPages    int    `json:"totalPages"`
}

// NotificationActivity represents a single notification activity item.
type NotificationActivity struct {
	Title     string `json:"title"`
	Contents  string `json:"contents"`
	CreatedAt string `json:"regDate"`
	Category  string `json:"notifyCategory"`
}

// NotificationActivitiesResponse wraps the list of notification activities.
type NotificationActivitiesResponse struct {
	Activities []NotificationActivity `json:"notifyActivities"`
}
