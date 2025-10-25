# Elder Licensing

Elder uses a **Limited AGPL v3** license with a preamble for fair use.

## License Overview

- **License**: AGPL v3 (Affero General Public License)
- **Copyright**: Penguin Technologies Group LLC
- **Restrictions**: Limited by preamble

## Full License

See [LICENSE.md](../LICENSE.md) for the complete license text.

## License Tiers

Elder integrates with the PenguinTech License Server for feature gating:

| Tier | Cost | Features | Limits |
|------|------|----------|--------|
| **Community** | Free | Basic tracking, local auth, REST API | Up to 100 entities |
| **Professional** | Paid | + SAML/OAuth2, advanced visualization | Unlimited entities |
| **Enterprise** | Paid | + All features, LDAP, gRPC API, audit logging, SSO | Unlimited |

## PenguinTech License Server

Elder uses the centralized [PenguinTech License Server](https://license.penguintech.io) for:

- Feature gating based on license tier
- Usage tracking and reporting
- License validation
- Compliance audit logging

### License Key Format

```
PENG-XXXX-XXXX-XXXX-XXXX-XXXX
```

### Configuration

```bash
# In .env
LICENSE_KEY=PENG-XXXX-XXXX-XXXX-XXXX-XXXX
PRODUCT_NAME=elder
LICENSE_SERVER_URL=https://license.penguintech.io
```

## Feature Comparison

### Community Tier (Free)

✅ **Included:**
- Organizations (hierarchical)
- Entities (all types)
- Dependencies
- Issues and projects
- REST API
- Web UI
- Basic authentication (local)
- Prometheus metrics
- Up to 100 entities

❌ **Not Included:**
- SAML/OAuth2 SSO
- LDAP integration
- gRPC API
- Advanced audit logging
- Priority support

### Professional Tier

✅ **Everything in Community, plus:**
- Unlimited entities
- SAML/OAuth2 SSO
- Advanced visualization
- Enhanced graph features
- Email support
- SLA guarantee

❌ **Enterprise Features:**
- LDAP sync
- gRPC API
- Connector service
- Advanced audit logging
- Priority support

### Enterprise Tier

✅ **Everything, including:**
- All Professional features
- LDAP/LDAPS integration
- gRPC API (high-performance)
- Connector Service (AWS, GCP, Workspace, LDAP sync)
- Advanced audit logging
- Compliance reporting (SOC2, ISO27001)
- White-label capabilities
- Priority support
- Dedicated account manager
- Custom development available

## License Validation

Elder validates licenses on startup and periodically:

```python
# License validation happens automatically
# Degraded features if license invalid:
# - Enterprise → Professional
# - Professional → Community
# - Expired → Community (grace period)
```

## Obtaining a License

### Community (Free)

No license key required. Simply install and run Elder.

### Professional / Enterprise

1. Visit [https://elder.penguintech.io](https://elder.penguintech.io)
2. Choose your tier
3. Complete purchase
4. Receive license key via email
5. Configure in Elder

Or contact sales:
- **Email**: sales@penguintech.io
- **Phone**: TBD

## License Integration

### How It Works

1. **Startup**: Elder validates license with PenguinTech License Server
2. **Keepalive**: Periodic validation (hourly)
3. **Feature Gating**: Features enabled/disabled based on tier
4. **Graceful Degradation**: Invalid license → downgrade to Community

### License Client

```python
from shared.licensing import license_client

# Validate license
validation = license_client.validate()

# Check feature
if license_client.check_feature("advanced_analytics"):
    # Feature available
    pass

# Send usage data
license_client.keepalive(usage_data={
    "active_users": 50,
    "entities": 5000
})
```

## Compliance

### AGPL Requirements

If you modify Elder and provide it as a service:

1. **Source Code**: Must provide source code to users
2. **License Notice**: Must include license in modified versions
3. **Network Use**: AGPL covers network use (not just distribution)

### Fair Use Preamble

The license includes a fair use preamble that:

- Allows evaluation and testing
- Permits educational use
- Supports research purposes
- Defines acceptable use cases

See [LICENSE.md](../LICENSE.md) for details.

## Contributing

By contributing to Elder, you agree that:

1. Your contributions will be licensed under the same Limited AGPL v3
2. You have the right to submit the contribution
3. You understand Penguin Technologies Group LLC owns the project

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Questions

### Can I use Elder commercially?

Yes, with appropriate licensing:
- **Internal use**: Community tier is fine
- **Service provider**: Professional or Enterprise tier required
- **Modifications**: Must comply with AGPL terms

### Do I need a license for development?

No. Development and testing can use Community tier.

### Can I resell Elder?

No. Elder is provided by Penguin Technologies Group LLC.
You can provide consulting services around Elder.

### What happens if my license expires?

- **Grace Period**: 30 days
- **Degradation**: After grace, downgrades to Community tier
- **Data**: No data loss, only feature restrictions

### Can I transfer my license?

Enterprise licenses are transferable with approval.
Contact sales@penguintech.io.

## Support

### Community Support

- GitHub Issues
- GitHub Discussions
- Documentation

### Professional Support

- Email support
- 48-hour response time
- Bug fix priority

### Enterprise Support

- Priority email + phone
- 4-hour response time (business hours)
- Dedicated support engineer
- Custom development available

## Resources

- **License Server**: https://license.penguintech.io
- **Product Website**: https://elder.penguintech.io
- **Documentation**: https://elder-docs.penguintech.io
- **Company**: https://www.penguintech.io
- **Sales**: sales@penguintech.io
- **Support**: support@penguintech.io

## License Text

Full license text available at [LICENSE.md](../LICENSE.md).
