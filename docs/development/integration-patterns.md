## Common Integration Patterns

### License-Gated Features
```python
# Python feature gating
from shared.licensing import license_client, requires_feature

@requires_feature("advanced_analytics")
def generate_advanced_report():
    """This feature requires professional+ license"""
    return advanced_analytics.generate_report()

# Startup validation
def initialize_application():
    client = license_client.get_client()
    validation = client.validate()
    if not validation.get("valid"):
        logger.error(f"License validation failed: {validation.get('message')}")
        sys.exit(1)

    logger.info(f"License valid for {validation['customer']} ({validation['tier']})")
    return validation
```

```go
// Go feature gating
package main

import (
    "log"
    "os"
    "your-project/internal/license"
)

func main() {
    client := license.NewClient(os.Getenv("LICENSE_KEY"), "your-product")

    validation, err := client.Validate()
    if err != nil || !validation.Valid {
        log.Fatal("License validation failed")
    }

    log.Printf("License valid for %s (%s)", validation.Customer, validation.Tier)

    // Check features
    if hasAdvanced, _ := client.CheckFeature("advanced_feature"); hasAdvanced {
        log.Println("Advanced features enabled")
    }
}
```

### Database Integration
```python
# Python with SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

```go
// Go with GORM
import "gorm.io/gorm"

type User struct {
    ID    uint   `gorm:"primaryKey"`
    Name  string `gorm:"not null"`
    Email string `gorm:"uniqueIndex;not null"`
}
```

### API Development
```python
# Python with Flask
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from apps.api.models import User
from shared.database import db

bp = Blueprint("users", __name__)

@bp.route('/users', methods=['GET', 'POST'])
@cross_origin()
def api_users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify({'users': [u.to_dict() for u in users]})
    # Handle POST...
```

```go
// Go with Gin
func setupRoutes() *gin.Engine {
    r := gin.Default()
    r.Use(cors.Default())

    v1 := r.Group("/api/v1")
    {
        v1.GET("/users", getUsers)
        v1.POST("/users", createUser)
    }
    return r
}
```

### Monitoring Integration
```python
# Python metrics with Flask
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Metrics are automatically collected and exposed at /metrics
# Custom metrics can be added:
metrics.info('app_info', 'Application info', version='1.0.0')
```

```go
// Go metrics
import "github.com/prometheus/client_golang/prometheus"

var (
    requestCount = prometheus.NewCounterVec(
        prometheus.CounterOpts{Name: "http_requests_total"},
        []string{"method", "endpoint"})
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{Name: "http_request_duration_seconds"},
        []string{"method", "endpoint"})
)
```

