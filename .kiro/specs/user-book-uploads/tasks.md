# Implementation Plan

- [ ] 1. Set up database infrastructure and models
  - Create SQLite database schema with proper tables and relationships
  - Implement database connection management with connection pooling
  - Create data models using dataclasses for User, Book, UserSettings, and related entities
  - Write database migration utilities to convert existing JSON data to SQLite
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 2. Implement enhanced database manager
  - [ ] 2.1 Create core database operations for users and books
    - Write async methods for user CRUD operations (create_user, get_user_by_telegram_id, update_user)
    - Implement book CRUD operations (create_book, get_user_books, get_book_by_id, update_book, delete_book)
    - Add methods for managing active book selection (set_active_book, get_active_book)
    - Write unit tests for all database operations
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 2.2 Implement reading progress and gamification features
    - Create methods for updating reading progress (update_reading_progress, complete_book)
    - Implement achievement system database operations (unlock_achievement, get_user_achievements)
    - Add reading session tracking (add_reading_session, get_reading_stats)
    - Write comprehensive tests for gamification features
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. Create file management system
  - [ ] 3.1 Implement secure file storage structure
    - Create FileManager class with user-specific directory management
    - Implement methods for creating and managing user directories (get_user_directory, get_user_books_directory)
    - Add secure file path validation to prevent path traversal attacks
    - Write file permission management utilities
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ] 3.2 Implement file upload and storage operations
    - Create methods for storing uploaded files securely (store_uploaded_file)
    - Implement unique filename generation to handle duplicates (generate_unique_filename)
    - Add file deletion and cleanup utilities (delete_user_file, cleanup_user_files)
    - Write comprehensive tests for file operations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2_

- [ ] 4. Build upload service and validation
  - [ ] 4.1 Create comprehensive file validation system
    - Enhance FileValidator class with stricter PDF validation
    - Implement file size, format, and content validation
    - Add security checks for malicious files and encrypted PDFs
    - Create validation result models with detailed error reporting
    - _Requirements: 1.1, 6.1, 6.4, 7.5_

  - [ ] 4.2 Implement upload processing service
    - Create UploadService class for handling file upload workflow
    - Implement async file processing with progress tracking
    - Add metadata extraction from PDF files (title, page count)
    - Create error handling and rollback mechanisms for failed uploads
    - _Requirements: 1.1, 1.2, 1.3, 6.2, 6.3, 7.1_

- [ ] 5. Enhance PDF reader for multi-user support
  - [ ] 5.1 Modify PDFReader for user-specific operations
    - Update PDFReader constructor to work with user_id and book_id
    - Implement user-specific image output directories
    - Add methods for getting user's active book PDF reader
    - Create book-specific page extraction methods
    - _Requirements: 3.1, 3.2, 3.3, 7.2, 7.3_

  - [ ] 5.2 Implement efficient image processing
    - Add memory-efficient page extraction for large PDFs
    - Implement user and book-specific image cleanup
    - Create caching mechanisms for frequently accessed pages
    - Add image compression and quality optimization
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 6. Create book management service
  - [ ] 6.1 Implement core book management operations
    - Create BookService class with user library management
    - Implement methods for book upload, selection, and deletion
    - Add book metadata management and display
    - Create book completion tracking and statistics
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ] 6.2 Add book switching and progress management
    - Implement active book selection with progress preservation
    - Create methods for switching between multiple books
    - Add reading progress synchronization across book changes
    - Implement book completion detection and celebration
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 7. Update bot handlers for multi-book support
  - [ ] 7.1 Modify existing command handlers
    - Update /start handler to check for user books and prompt upload if needed
    - Modify /status handler to show active book information and library summary
    - Update /next and /current handlers to work with active book
    - Enhance /goto handler to work with user's active book
    - _Requirements: 2.5, 3.3, 3.5_

  - [ ] 7.2 Create new book management commands
    - Implement /library command to show user's book collection
    - Create /select command for choosing active book from library
    - Add /delete command for removing books from user library
    - Implement /book command to show detailed book information
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 7.3 Enhance upload command and flow
    - Update /upload command with improved user guidance and feedback
    - Implement progress indicators for large file uploads
    - Add upload validation feedback with specific error messages
    - Create upload success confirmation with book details
    - _Requirements: 1.1, 1.2, 1.5, 6.1, 6.2, 6.3_

- [ ] 8. Update keyboard interfaces and user experience
  - [ ] 8.1 Create book management keyboards
    - Add library browsing keyboard with book selection options
    - Create book management keyboard (select, delete, info)
    - Implement book upload keyboard with guidance and options
    - Add book switching keyboard for quick active book changes
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 8.2 Update existing keyboards for multi-book support
    - Modify main menu to include library access
    - Update status keyboard to show active book options
    - Enhance settings keyboard with book-specific options
    - Add reading progress keyboard with book context
    - _Requirements: 2.5, 3.3, 3.5_

- [ ] 9. Implement data migration system
  - [ ] 9.1 Create JSON to SQLite migration
    - Write migration script to convert existing JSON database to SQLite
    - Implement data validation during migration process
    - Create backup and rollback mechanisms for safe migration
    - Add migration progress tracking and error reporting
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 9.2 Handle file system reorganization
    - Create script to move existing files to new user-specific structure
    - Update file paths in database during migration
    - Implement cleanup of old file structure after successful migration
    - Add verification of file integrity after migration
    - _Requirements: 5.1, 5.2, 5.3_

- [ ] 10. Add comprehensive error handling and logging
  - [ ] 10.1 Implement error handling for upload operations
    - Create custom exception classes for different error types
    - Add comprehensive error logging with user context
    - Implement user-friendly error messages for common issues
    - Create error recovery mechanisms for partial failures
    - _Requirements: 6.1, 6.4, 7.5_

  - [ ] 10.2 Add system monitoring and cleanup
    - Implement disk space monitoring and alerts
    - Create automated cleanup for orphaned files and images
    - Add performance monitoring for upload and processing operations
    - Implement health checks for database and file system
    - _Requirements: 5.4, 7.1, 7.2_

- [ ] 11. Create comprehensive test suite
  - [ ] 11.1 Write unit tests for core components
    - Create tests for database operations with SQLite in-memory database
    - Write tests for file management operations with temporary directories
    - Add tests for upload validation and processing
    - Create tests for PDF reader enhancements
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ] 11.2 Implement integration tests
    - Create end-to-end tests for complete upload workflow
    - Write tests for multi-user scenarios and data isolation
    - Add tests for migration from JSON to SQLite
    - Create performance tests for large file handling
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 12. Update configuration and deployment
  - [ ] 12.1 Update configuration management
    - Add database configuration options to config.py
    - Create file storage configuration with user directory settings
    - Add upload limits and validation settings
    - Update environment variable handling for new features
    - _Requirements: 4.1, 4.5, 5.1, 7.5_

  - [ ] 12.2 Update deployment and documentation
    - Update Docker configuration for new database requirements
    - Create database initialization scripts for deployment
    - Update README with new features and setup instructions
    - Add migration guide for existing installations
    - _Requirements: 4.1, 4.2, 4.3, 4.4_