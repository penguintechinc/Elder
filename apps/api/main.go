package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/penguintechinc/project-template/shared/licensing"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	// Prometheus metrics
	requestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status"},
	)

	requestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "http_request_duration_seconds",
			Help: "HTTP request duration in seconds",
		},
		[]string{"method", "endpoint"},
	)
)

func init() {
	// Register Prometheus metrics
	prometheus.MustRegister(requestsTotal)
	prometheus.MustRegister(requestDuration)
}

func main() {
	// Initialize license client
	licenseClient := licensing.NewClientFromEnv()
	if licenseClient == nil {
		log.Fatal("LICENSE_KEY and PRODUCT_NAME environment variables are required")
	}

	// Validate license on startup
	validation, err := licenseClient.Validate()
	if err != nil {
		log.Fatalf("License validation failed: %v", err)
	}

	if !validation.Valid {
		log.Fatalf("Invalid license: %s", validation.Message)
	}

	log.Printf("License valid for %s (%s tier)", validation.Customer, validation.Tier)

	// Log available features
	for _, feature := range validation.Features {
		if feature.Entitled {
			log.Printf("Feature enabled: %s", feature.Name)
		}
	}

	// Set up Gin router
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	// Add license middleware
	r.Use(licensing.LicenseMiddleware(licenseClient))

	// Add metrics middleware
	r.Use(func(c *gin.Context) {
		timer := prometheus.NewTimer(requestDuration.WithLabelValues(c.Request.Method, c.FullPath()))
		defer timer.ObserveDuration()

		c.Next()

		requestsTotal.WithLabelValues(
			c.Request.Method,
			c.FullPath(),
			string(rune(c.Writer.Status())),
		).Inc()
	})

	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"version": os.Getenv("VERSION"),
		})
	})

	// Metrics endpoint
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// API routes
	v1 := r.Group("/api/v1")
	{
		v1.GET("/status", getStatus)
		v1.GET("/features", getFeatures)

		// Feature-gated endpoints
		fg := licensing.NewFeatureGate(licenseClient)

		advanced := v1.Group("/advanced")
		advanced.Use(fg.RequireFeature("advanced_analytics"))
		{
			advanced.GET("/analytics", getAdvancedAnalytics)
		}

		enterprise := v1.Group("/enterprise")
		enterprise.Use(fg.RequireFeature("enterprise_features"))
		{
			enterprise.GET("/reports", getEnterpriseReports)
		}
	}

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Starting server on port %s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

func getStatus(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "ok",
		"timestamp": "2025-01-01T00:00:00Z",
		"version":   os.Getenv("VERSION"),
	})
}

func getFeatures(c *gin.Context) {
	fg, err := licensing.GetFeatureGate(c)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	features := fg.GetAllFeatures()
	c.JSON(http.StatusOK, gin.H{
		"features": features,
	})
}

func getAdvancedAnalytics(c *gin.Context) {
	// This endpoint requires advanced_analytics feature
	c.JSON(http.StatusOK, gin.H{
		"message": "Advanced analytics data",
		"data":    []string{"metric1", "metric2", "metric3"},
	})
}

func getEnterpriseReports(c *gin.Context) {
	// This endpoint requires enterprise_features
	c.JSON(http.StatusOK, gin.H{
		"message": "Enterprise reports",
		"reports": []string{"security_audit", "compliance_report", "usage_analytics"},
	})
}