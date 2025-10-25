# Elder Documentation

Welcome to the Elder infrastructure management platform documentation.

## Table of Contents

### Getting Started
- [Contributing](CONTRIBUTING.md) - How to contribute to Elder
- [Usage](USAGE.md) - Basic usage instructions
- [Database](DATABASE.md) - Database schema and design
- [Release Notes](RELEASE_NOTES.md) - Version history and changes

### Core Documentation

#### API
- [API Documentation](api/) - REST API reference and endpoints

#### Architecture
- [Architecture](architecture/) - System design and architecture decisions

#### Development
- [Development Setup](development/) - Local development environment setup

#### Deployment
- [Deployment Guide](deployment/) - Production deployment instructions

#### Licensing
- [Licensing](licensing/) - License integration and management
- [License Information](LICENSE.md) - Full license text

### Services & Features

#### Connector Service
The Elder Connector Service synchronizes data from external sources into Elder.

- **[Quick Start Guide](connector/QUICKSTART.md)** - Get started in 5 minutes
- **[Complete Reference](connector/README.md)** - Full documentation and usage
- **[Implementation Details](connector/IMPLEMENTATION.md)** - Architecture and design

**Supported Integrations:**
- AWS (EC2, VPC, S3)
- GCP (Compute Engine, VPC Networks, Cloud Storage)
- Google Workspace (Users, Groups, Organizational Units)
- LDAP/LDAPS (Users, Groups, Organizational Units)

#### gRPC
- [gRPC Documentation](grpc/) - gRPC API reference

#### Logging
- [Logging](logging/) - Logging configuration and best practices

## Documentation Structure

```
docs/
├── README.md                    # This file
├── CONTRIBUTING.md              # Contribution guidelines
├── USAGE.md                     # Basic usage
├── DATABASE.md                  # Database documentation
├── LICENSE.md                   # License information
├── RELEASE_NOTES.md            # Version history
├── api/                        # API documentation
├── architecture/               # Architecture docs
├── connector/                  # Connector service docs
│   ├── README.md              # Complete reference
│   ├── QUICKSTART.md          # 5-minute setup guide
│   └── IMPLEMENTATION.md      # Technical details
├── deployment/                 # Deployment guides
├── development/                # Development setup
├── grpc/                       # gRPC documentation
├── licensing/                  # License integration
└── logging/                    # Logging documentation
```

## Quick Links

### For Users
- [Getting Started](USAGE.md)
- [Connector Quick Start](connector/QUICKSTART.md)
- [API Documentation](api/)

### For Developers
- [Development Setup](development/)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Architecture Overview](architecture/)

### For Operators
- [Deployment Guide](deployment/)
- [Database Schema](DATABASE.md)
- [Monitoring & Logging](logging/)

## Getting Help

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Browse the docs in this directory
- **Community**: Join discussions and ask questions

## License

Elder is licensed under a Limited AGPL3 license with preamble for fair use.
See [LICENSE.md](LICENSE.md) for complete details.

---

**Maintained by**: Penguin Tech Inc
**Project**: Elder Infrastructure Management Platform
