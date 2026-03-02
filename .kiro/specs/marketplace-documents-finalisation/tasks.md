# Tasks: Finalisation Marketplace Documents Techniques

## Phase 1: Frontend - Pages Critiques (Priority 1)

### 1.1 Create PurchaseHistory Component
- [x] 1.1.1 Create PurchaseHistory.tsx component file
- [x] 1.1.2 Implement purchase list display with cards
- [x] 1.1.3 Add filter sidebar (date, culture, status, expired)
- [x] 1.1.4 Implement fetchPurchaseHistory API call with filters
- [ ] 1.1.5 Add regenerate link button and functionality
- [x] 1.1.6 Add download button with token handling
- [x] 1.1.7 Implement status badges (Payé, En attente, Échoué, Expiré)
- [x] 1.1.8 Add pagination controls
- [x] 1.1.9 Implement loading states with skeletons
- [x] 1.1.10 Add error handling with toast notifications
- [x] 1.1.11 Create purchase-history.css stylesheet
- [x] 1.1.12 Add route to App.tsx

### 1.2 Create PaymentSuccess Component
- [x] 1.2.1 Create PaymentSuccess.tsx component file
- [x] 1.2.2 Implement transaction_id extraction from URL params
- [x] 1.2.3 Add payment verification API call
- [x] 1.2.4 Display success animation and document details
- [x] 1.2.5 Add immediate download button
- [x] 1.2.6 Display expiration date (48h)
- [x] 1.2.7 Add link to purchase history
- [x] 1.2.8 Implement payment failure handling
- [x] 1.2.9 Add redirect logic for invalid transaction_id
- [x] 1.2.10 Create payment-success.css stylesheet
- [x] 1.2.11 Add route to App.tsx

### 1.3 Enhance Documents Component
- [x] 1.3.1 Add "already purchased" indicator check
- [x] 1.3.2 Create purchase confirmation modal
- [x] 1.3.3 Add modal with document details and confirm/cancel buttons
- [x] 1.3.4 Implement toast notifications for errors
- [x] 1.3.5 Add skeleton loaders for loading state
- [x] 1.3.6 Change button to "Télécharger" if already purchased
- [x] 1.3.7 Implement direct download for owned documents
- [x] 1.3.8 Update documents.css with new styles


### 1.4 Add Toast Notification System
- [x] 1.4.1 Custom toast system implemented (no external package needed)
- [x] 1.4.2 Toast components integrated in all pages
- [x] 1.4.3 Toast utility functions created (success, error, info, warning)
- [x] 1.4.4 Toast styles added to theme.css

### 1.5 Frontend Testing
- [ ] 1.5.1 Write unit tests for PurchaseHistory component
- [ ] 1.5.2 Write unit tests for PaymentSuccess component
- [ ] 1.5.3 Write unit tests for Documents enhancements
- [ ] 1.5.4 Test responsive design on mobile/tablet/desktop
- [ ] 1.5.5 Test all user flows manually

## Phase 2: Backend - Email Service (Priority 2)

### 2.1 Create EmailService
- [x] 2.1.1 Create apps/documents/services/email_service.py
- [x] 2.1.2 Implement EmailService class
- [x] 2.1.3 Implement send_purchase_confirmation() method
- [x] 2.1.4 Implement send_expiration_reminder() method
- [x] 2.1.5 Implement send_link_regenerated() method
- [x] 2.1.6 Add _render_email_template() helper method
- [x] 2.1.7 Add comprehensive logging
- [x] 2.1.8 Add error handling with graceful failures

### 2.2 Create Email Templates
- [x] 2.2.1 Create templates/emails/ directory
- [x] 2.2.2 Create base_email.html template with branding (Haroo)
- [x] 2.2.3 Create purchase_confirmation.html template
- [x] 2.2.4 Create purchase_confirmation.txt template
- [x] 2.2.5 Create expiration_reminder.html template
- [x] 2.2.6 Create expiration_reminder.txt template
- [x] 2.2.7 Create link_regenerated.html template
- [x] 2.2.8 Create link_regenerated.txt template
- [x] 2.2.9 Test templates with premailer for inline CSS (premailer intégré dans EmailService)
- [ ] 2.2.10 Test templates on Gmail, Outlook, Apple Mail (voir EMAIL_TESTING_GUIDE.md)

### 2.3 Configure Celery
- [x] 2.3.1 Install celery and redis packages (déjà installé dans requirements.txt)
- [x] 2.3.2 Configure Celery in haroo/celery.py (Beat schedule, timezone, retry config)
- [x] 2.3.3 Create send_purchase_confirmation_async task (avec retry exponential backoff)
- [x] 2.3.4 Create send_expiration_reminders scheduled task (toutes les heures)
- [x] 2.3.5 Create anonymize_old_download_logs scheduled task (quotidien à 2h00)
- [x] 2.3.6 Configure Celery Beat schedule (3 tâches planifiées configurées)
- [x] 2.3.7 Add retry logic with exponential backoff (max 3 retries, backoff max 600s)
- [x] 2.3.8 Test Celery tasks locally (test_celery_tasks.py créé)

### 2.4 Integrate Email Service
- [ ] 2.4.1 Call EmailService after successful payment in views.py
- [ ] 2.4.2 Call EmailService after link regeneration in views.py
- [ ] 2.4.3 Update settings.py with email configuration
- [ ] 2.4.4 Add FRONTEND_URL to settings
- [ ] 2.4.5 Test email sending in development with MailHog

### 2.5 Email Service Testing
- [ ] 2.5.1 Write unit tests for EmailService methods
- [ ] 2.5.2 Write tests for email template rendering
- [ ] 2.5.3 Write tests for Celery tasks
- [ ] 2.5.4 Write integration tests with MailHog
- [ ] 2.5.5 Test email delivery in staging environment


## Phase 3: Backend - Admin Improvements (Priority 3)

### 3.1 Enhance AchatDocumentAdmin
- [ ] 3.1.1 Update apps/documents/admin.py
- [ ] 3.1.2 Add custom list_display with links and badges
- [ ] 3.1.3 Implement acheteur_link() method
- [ ] 3.1.4 Implement document_link() method
- [ ] 3.1.5 Implement montant() method with FCFA formatting
- [ ] 3.1.6 Implement statut_badge() method with colors
- [ ] 3.1.7 Implement lien_statut() method with icons
- [ ] 3.1.8 Add list_filter for status, date, culture, region
- [ ] 3.1.9 Add search_fields for acheteur, document, transaction
- [ ] 3.1.10 Implement regenerate_links() admin action
- [ ] 3.1.11 Implement export_to_csv() admin action
- [ ] 3.1.12 Override changelist_view() to add statistics
- [ ] 3.1.13 Create admin template for statistics display

### 3.2 Enhance DocumentTechniqueAdmin
- [ ] 3.2.1 Add purchase_count display field
- [ ] 3.2.2 Add link to related purchases
- [ ] 3.2.3 Add activate/deactivate admin actions
- [ ] 3.2.4 Add filters by region, culture, actif, template
- [ ] 3.2.5 Improve search_fields

### 3.3 Enhance DocumentTemplateAdmin
- [ ] 3.3.1 Add duplicate_template() admin action
- [ ] 3.3.2 Display variables_requises as readonly formatted JSON
- [ ] 3.3.3 Add filters by type_document, format_fichier
- [ ] 3.3.4 Add version display in list

### 3.4 Admin Testing
- [ ] 3.4.1 Test all admin actions manually
- [ ] 3.4.2 Test statistics display
- [ ] 3.4.3 Test CSV export functionality
- [ ] 3.4.4 Test filters and search
- [ ] 3.4.5 Verify permissions and access control

## Phase 4: Backend - API Enhancements (Priority 2)

### 4.1 Add Payment Verification Endpoint
- [ ] 4.1.1 Create verify_payment() view in views.py
- [ ] 4.1.2 Add route GET /api/v1/purchases/verify/{transaction_id}
- [ ] 4.1.3 Implement transaction status check
- [ ] 4.1.4 Return document details and download link
- [ ] 4.1.5 Handle failed payments
- [ ] 4.1.6 Add authentication requirement
- [ ] 4.1.7 Write unit tests

### 4.2 Enhance Purchase History Endpoint
- [ ] 4.2.1 Verify PurchaseHistoryViewSet is complete
- [ ] 4.2.2 Test all filters (date, culture, status, expired)
- [ ] 4.2.3 Test pagination
- [ ] 4.2.4 Test search functionality
- [ ] 4.2.5 Optimize queries with select_related()
- [ ] 4.2.6 Add caching if needed

### 4.3 API Documentation
- [ ] 4.3.1 Install drf-spectacular for OpenAPI
- [ ] 4.3.2 Add schema decorators to all endpoints
- [ ] 4.3.3 Generate OpenAPI schema
- [ ] 4.3.4 Test Swagger UI
- [ ] 4.3.5 Document authentication requirements


## Phase 5: Testing (Priority 4 - Optional)

### 5.1 Backend Unit Tests
- [ ] 5.1.1 Write tests for SecureDownloadService
  - [ ] test_generate_download_token_length
  - [ ] test_generate_signed_url_creates_token
  - [ ] test_is_link_expired_with_expired_link
  - [ ] test_validate_download_token_success
  - [ ] test_validate_download_token_wrong_user
  - [ ] test_validate_download_token_unpaid
  - [ ] test_regenerate_link_creates_new_token
- [ ] 5.1.2 Write tests for EmailService
  - [ ] test_send_purchase_confirmation_success
  - [ ] test_send_purchase_confirmation_invalid_email
  - [ ] test_send_expiration_reminder
  - [ ] test_send_link_regenerated
  - [ ] test_email_template_rendering
- [ ] 5.1.3 Write tests for ViewSets
  - [ ] test_purchase_creates_transaction
  - [ ] test_purchase_already_owned
  - [ ] test_purchase_inactive_document
  - [ ] test_download_with_valid_token
  - [ ] test_download_with_expired_token
  - [ ] test_regenerate_link_success
  - [ ] test_purchase_history_filters
- [ ] 5.1.4 Run pytest with coverage report
- [ ] 5.1.5 Ensure coverage ≥ 80%

### 5.2 Frontend Unit Tests
- [ ] 5.2.1 Write tests for PurchaseHistory
  - [ ] test_renders_purchase_list
  - [ ] test_filters_apply_correctly
  - [ ] test_regenerate_button_visible_when_expired
  - [ ] test_download_button_opens_new_tab
  - [ ] test_loading_state_displayed
  - [ ] test_empty_state_displayed
- [ ] 5.2.2 Write tests for PaymentSuccess
  - [ ] test_fetches_payment_data_on_mount
  - [ ] test_displays_document_info
  - [ ] test_download_button_functional
  - [ ] test_redirects_on_failed_payment
  - [ ] test_redirects_without_transaction_id
- [ ] 5.2.3 Write tests for Documents enhancements
  - [ ] test_purchase_modal_opens
  - [ ] test_already_purchased_indicator
  - [ ] test_error_handling_on_purchase_failure
- [ ] 5.2.4 Run vitest with coverage report
- [ ] 5.2.5 Ensure coverage ≥ 70%

### 5.3 Property-Based Tests
- [ ] 5.3.1 Write property test: token uniqueness (Hypothesis)
- [ ] 5.3.2 Write property test: link expiration consistency (Hypothesis)
- [ ] 5.3.3 Write property test: download authorization invariant (Hypothesis)
- [ ] 5.3.4 Write property test: filter combinations produce valid URLs (fast-check)
- [ ] 5.3.5 Write property test: purchase list sorting invariant (fast-check)
- [ ] 5.3.6 Run all property tests with 100+ cases each

### 5.4 Integration Tests
- [ ] 5.4.1 Write test: complete purchase flow
- [ ] 5.4.2 Write test: link regeneration flow
- [ ] 5.4.3 Write test: filter purchase history
- [ ] 5.4.4 Write test: email sending with MailHog
- [ ] 5.4.5 Run integration tests in isolated environment

### 5.5 E2E Tests (Optional)
- [ ] 5.5.1 Install Playwright
- [ ] 5.5.2 Write E2E test: complete purchase and download flow
- [ ] 5.5.3 Write E2E test: regenerate expired download link
- [ ] 5.5.4 Write E2E test: filter purchase history
- [ ] 5.5.5 Run E2E tests in staging environment


## Phase 6: Performance Optimization (Priority 3)

### 6.1 Database Optimization
- [ ] 6.1.1 Add index on AchatDocument.expiration_lien
- [ ] 6.1.2 Add index on AchatDocument (transaction, created_at)
- [ ] 6.1.3 Verify all select_related() usage
- [ ] 6.1.4 Run EXPLAIN ANALYZE on slow queries
- [ ] 6.1.5 Optimize N+1 queries if found

### 6.2 Caching Implementation
- [ ] 6.2.1 Add Redis caching for purchase history
- [ ] 6.2.2 Implement cache invalidation on purchase/regeneration
- [ ] 6.2.3 Add cache for "already purchased" checks
- [ ] 6.2.4 Test cache hit rates
- [ ] 6.2.5 Monitor cache performance

### 6.3 File Serving Optimization
- [ ] 6.3.1 Configure Nginx X-Accel-Redirect
- [ ] 6.3.2 Update download view to use X-Accel-Redirect
- [ ] 6.3.3 Test file download performance
- [ ] 6.3.4 Verify memory usage during downloads

### 6.4 Frontend Optimization
- [ ] 6.4.1 Implement code splitting for PurchaseHistory
- [ ] 6.4.2 Implement code splitting for PaymentSuccess
- [ ] 6.4.3 Add debouncing to filter inputs (300ms)
- [ ] 6.4.4 Implement optimistic UI updates
- [ ] 6.4.5 Optimize bundle size
- [ ] 6.4.6 Test Lighthouse scores

## Phase 7: Security Hardening (Priority 2)

### 7.1 Token Security
- [ ] 7.1.1 Verify token generation uses secrets.token_urlsafe()
- [ ] 7.1.2 Verify token length ≥ 32 characters
- [ ] 7.1.3 Add token uniqueness constraint in database
- [ ] 7.1.4 Mask tokens in admin interface
- [ ] 7.1.5 Add rate limiting to download endpoint

### 7.2 Payment Security
- [ ] 7.2.1 Implement Fedapay webhook signature verification
- [ ] 7.2.2 Add CSRF exemption for webhook endpoint only
- [ ] 7.2.3 Validate all transaction data from Fedapay
- [ ] 7.2.4 Log all payment attempts with IP

### 7.3 Email Security
- [ ] 7.3.1 Validate email addresses before sending
- [ ] 7.3.2 Sanitize user content in emails
- [ ] 7.3.3 Configure SPF records for domain
- [ ] 7.3.4 Enable DKIM signing

### 7.4 Input Validation
- [ ] 7.4.1 Add frontend validation for all forms
- [ ] 7.4.2 Add backend validation with DRF serializers
- [ ] 7.4.3 Sanitize file uploads
- [ ] 7.4.4 Add XSS protection
- [ ] 7.4.5 Test with OWASP ZAP

### 7.5 Data Privacy
- [ ] 7.5.1 Implement data export for users
- [ ] 7.5.2 Implement data deletion on account closure
- [ ] 7.5.3 Create anonymize_old_download_logs task
- [ ] 7.5.4 Document data retention policy
- [ ] 7.5.5 Add privacy policy page


## Phase 8: Documentation (Priority 3)

### 8.1 Code Documentation
- [ ] 8.1.1 Add docstrings to all EmailService methods
- [ ] 8.1.2 Add docstrings to all view methods
- [ ] 8.1.3 Add JSDoc to React components
- [ ] 8.1.4 Document all TypeScript interfaces
- [ ] 8.1.5 Add inline comments for complex logic

### 8.2 API Documentation
- [ ] 8.2.1 Generate OpenAPI schema with drf-spectacular
- [ ] 8.2.2 Add examples to all endpoints
- [ ] 8.2.3 Document authentication requirements
- [ ] 8.2.4 Document error codes and messages
- [ ] 8.2.5 Publish Swagger UI

### 8.3 User Documentation
- [ ] 8.3.1 Write user guide: "Comment acheter un document"
- [ ] 8.3.2 Write user guide: "Comment télécharger un document"
- [ ] 8.3.3 Write user guide: "Comment régénérer un lien expiré"
- [ ] 8.3.4 Create FAQ page
- [ ] 8.3.5 Add screenshots to guides
- [ ] 8.3.6 Translate to French

### 8.4 Admin Documentation
- [ ] 8.4.1 Write admin guide: "Gestion des documents"
- [ ] 8.4.2 Write admin guide: "Gestion des achats"
- [ ] 8.4.3 Write admin guide: "Régénération de liens"
- [ ] 8.4.4 Write admin guide: "Export de données"
- [ ] 8.4.5 Document common troubleshooting scenarios

### 8.5 Technical Documentation
- [ ] 8.5.1 Document architecture decisions
- [ ] 8.5.2 Document deployment process
- [ ] 8.5.3 Document backup and recovery procedures
- [ ] 8.5.4 Document monitoring and alerting setup
- [ ] 8.5.5 Create runbook for common issues

## Phase 9: Deployment Preparation (Priority 1)

### 9.1 Environment Setup
- [ ] 9.1.1 Configure staging environment
- [ ] 9.1.2 Configure production environment
- [ ] 9.1.3 Set up environment variables
- [ ] 9.1.4 Configure secrets management
- [ ] 9.1.5 Set up SSL certificates

### 9.2 Database Setup
- [ ] 9.2.1 Run migrations in staging
- [ ] 9.2.2 Verify data integrity
- [ ] 9.2.3 Set up database backups
- [ ] 9.2.4 Configure connection pooling
- [ ] 9.2.5 Test database failover

### 9.3 Service Configuration
- [ ] 9.3.1 Configure Nginx with X-Accel-Redirect
- [ ] 9.3.2 Configure Redis for caching and Celery
- [ ] 9.3.3 Configure Celery workers
- [ ] 9.3.4 Configure Celery Beat scheduler
- [ ] 9.3.5 Set up email SMTP server
- [ ] 9.3.6 Configure Fedapay production keys

### 9.4 Monitoring Setup
- [ ] 9.4.1 Set up Sentry for error tracking
- [ ] 9.4.2 Configure Prometheus metrics
- [ ] 9.4.3 Set up Grafana dashboards
- [ ] 9.4.4 Configure CloudWatch alarms
- [ ] 9.4.5 Set up log aggregation

### 9.5 Deployment
- [ ] 9.5.1 Deploy backend to staging
- [ ] 9.5.2 Deploy frontend to staging
- [ ] 9.5.3 Run smoke tests in staging
- [ ] 9.5.4 Deploy backend to production
- [ ] 9.5.5 Deploy frontend to production
- [ ] 9.5.6 Run smoke tests in production
- [ ] 9.5.7 Monitor for errors


## Phase 10: Post-Deployment (Priority 1)

### 10.1 Monitoring and Validation
- [ ] 10.1.1 Monitor error rates for 24 hours
- [ ] 10.1.2 Monitor API response times
- [ ] 10.1.3 Monitor email delivery rates
- [ ] 10.1.4 Check Celery task execution
- [ ] 10.1.5 Verify all features work in production

### 10.2 User Acceptance Testing
- [ ] 10.2.1 Test complete purchase flow with real payment
- [ ] 10.2.2 Test download functionality
- [ ] 10.2.3 Test link regeneration
- [ ] 10.2.4 Test email reception
- [ ] 10.2.5 Test admin interface
- [ ] 10.2.6 Collect user feedback

### 10.3 Performance Validation
- [ ] 10.3.1 Run load tests with 100 concurrent users
- [ ] 10.3.2 Verify page load times < 2s
- [ ] 10.3.3 Verify API response times < 500ms
- [ ] 10.3.4 Check database query performance
- [ ] 10.3.5 Monitor cache hit rates

### 10.4 Bug Fixes and Adjustments
- [ ] 10.4.1 Fix any critical bugs found
- [ ] 10.4.2 Address performance issues
- [ ] 10.4.3 Adjust UI based on feedback
- [ ] 10.4.4 Update documentation if needed
- [ ] 10.4.5 Deploy hotfixes if necessary

### 10.5 Final Validation
- [ ] 10.5.1 Verify all acceptance criteria met
- [ ] 10.5.2 Verify all functional requirements met
- [ ] 10.5.3 Verify all non-functional requirements met
- [ ] 10.5.4 Sign off from stakeholders
- [ ] 10.5.5 Close project

## Summary

**Total Tasks**: 200+
**Estimated Time**: 10-13 days
**Priority Breakdown**:
- Priority 1 (Critical): Phases 1, 9, 10 - 5-7 days
- Priority 2 (Important): Phases 2, 4, 7 - 3-4 days
- Priority 3 (Nice to have): Phases 3, 6, 8 - 2-3 days
- Priority 4 (Optional): Phase 5 - 3-4 days

**Dependencies**:
- Phase 1 can start immediately
- Phase 2 depends on Phase 1 completion
- Phase 3 can run in parallel with Phase 2
- Phase 4 can run in parallel with Phase 2
- Phase 5 depends on Phases 1-4 completion
- Phase 6 can run in parallel with Phase 5
- Phase 7 should be done before Phase 9
- Phase 8 can run in parallel with other phases
- Phase 9 depends on Phases 1-4 completion
- Phase 10 depends on Phase 9 completion

**Success Criteria**:
- ✅ All Priority 1 tasks completed
- ✅ All Priority 2 tasks completed
- ✅ 80%+ test coverage for backend
- ✅ 70%+ test coverage for frontend
- ✅ All acceptance criteria met
- ✅ Production deployment successful
- ✅ No critical bugs in production

