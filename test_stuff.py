#!/usr/bin/env python3
# quick script to test some functionality
# TODO: clean this up later (probably never will lol)

import sys
import os
sys.path.append('.')

from database_manager import DatabaseManager
from pdf_reader import PDFReader

def quick_test():
    """quick and dirty test function"""
    print("testing db connection...")
    
    db = DatabaseManager("test_db.json")
    
    # add fake user
    db.add_user(12345, "test_user")
    
    users = db.get_users()
    print(f"users in db: {len(users)}")
    
    # test pdf reader
    if os.path.exists("book.pdf"):
        print("found book.pdf, testing reader...")
        reader = PDFReader(pdf_path="book.pdf")
        total_pages = reader.get_total_pages()
        print(f"total pages: {total_pages}")
    else:
        print("no book.pdf found")

def test_config():
    """test config loading"""
    from config import get_config
    cfg = get_config()
    print(f"bot token: {cfg.bot_token[:10]}..." if cfg.bot_token != "dummy_token" else "using dummy token")
    print(f"pages per send: {cfg.pages_per_send}")

if __name__ == "__main__":
    print("=== quick test script ===")
    quick_test()
    test_config()
    print("done!")