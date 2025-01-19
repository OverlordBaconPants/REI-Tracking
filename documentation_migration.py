import json
import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def migrate_documentation(config):
    """
    Migrates transaction documentation to new structure and updates JSON schema
    """
    logger = setup_logging()
    logger.info("Starting documentation migration")
    
    try:
        # Create backup of transactions.json
        backup_path = f"{config.TRANSACTIONS_FILE}.bak"
        shutil.copy2(config.TRANSACTIONS_FILE, backup_path)
        logger.info(f"Created backup at {backup_path}")

        # Load transactions
        with open(config.TRANSACTIONS_FILE, 'r') as f:
            transactions = json.load(f)

        # Create unified uploads directory if it doesn't exist
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

        # Track files that were successfully migrated
        migrated_files = {
            'success': [],
            'failed': [],
            'skipped': []
        }

        # Process each transaction
        for transaction in transactions:
            transaction_id = transaction.get('id')
            
            # Handle main documentation file
            if 'documentation_file' in transaction and transaction['documentation_file']:
                old_filename = transaction['documentation_file']
                if old_filename:
                    try:
                        # Generate new filename with prefix
                        new_filename = f"trans_{transaction_id}_{Path(old_filename).name}"
                        
                        # Check both possible source locations
                        possible_sources = [
                            os.path.join(config.UPLOAD_FOLDER, old_filename),
                            os.path.join(config.REIMBURSEMENTS_DIR, old_filename)
                        ]
                        
                        source_path = None
                        for path in possible_sources:
                            if os.path.exists(path):
                                source_path = path
                                break
                        
                        if source_path:
                            # Move and rename file
                            new_path = os.path.join(config.UPLOAD_FOLDER, new_filename)
                            if os.path.exists(new_path):
                                logger.warning(f"File already exists at destination: {new_path}")
                                migrated_files['skipped'].append(old_filename)
                            else:
                                shutil.copy2(source_path, new_path)
                                transaction['documentation_file'] = new_filename
                                migrated_files['success'].append(old_filename)
                        else:
                            logger.warning(f"Source file not found: {old_filename}")
                            migrated_files['failed'].append(old_filename)
                    except Exception as e:
                        logger.error(f"Error processing file {old_filename}: {str(e)}")
                        migrated_files['failed'].append(old_filename)

            # Handle reimbursement documentation
            if 'reimbursement' in transaction and 'documentation' in transaction['reimbursement']:
                old_filename = transaction['reimbursement']['documentation']
                if old_filename:
                    try:
                        # Generate new filename with prefix
                        new_filename = f"reimb_{transaction_id}_{Path(old_filename).name}"
                        
                        # Check both possible source locations
                        possible_sources = [
                            os.path.join(config.REIMBURSEMENTS_DIR, old_filename),
                            os.path.join(config.UPLOAD_FOLDER, old_filename)
                        ]
                        
                        source_path = None
                        for path in possible_sources:
                            if os.path.exists(path):
                                source_path = path
                                break
                        
                        if source_path:
                            # Move and rename file
                            new_path = os.path.join(config.UPLOAD_FOLDER, new_filename)
                            if os.path.exists(new_path):
                                logger.warning(f"File already exists at destination: {new_path}")
                                migrated_files['skipped'].append(old_filename)
                            else:
                                shutil.copy2(source_path, new_path)
                                transaction['reimbursement']['documentation'] = new_filename
                                migrated_files['success'].append(old_filename)
                        else:
                            logger.warning(f"Source file not found: {old_filename}")
                            migrated_files['failed'].append(old_filename)
                    except Exception as e:
                        logger.error(f"Error processing file {old_filename}: {str(e)}")
                        migrated_files['failed'].append(old_filename)

        # Save updated transactions
        with open(config.TRANSACTIONS_FILE, 'w') as f:
            json.dump(transactions, f, indent=2)

        # Generate migration report
        logger.info("\nMigration Report:")
        logger.info(f"Successfully migrated: {len(migrated_files['success'])} files")
        logger.info(f"Failed to migrate: {len(migrated_files['failed'])} files")
        logger.info(f"Skipped files: {len(migrated_files['skipped'])} files")
        
        if migrated_files['failed']:
            logger.warning("\nFailed files:")
            for filename in migrated_files['failed']:
                logger.warning(f"- {filename}")

        return {
            'success': True,
            'migrated': migrated_files,
            'backup_path': backup_path
        }

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """
    Main function to run the migration
    """
    from config import get_config
    
    config = get_config()
    result = migrate_documentation(config)
    
    if result['success']:
        print("\nMigration completed successfully!")
        print(f"Backup saved at: {result['backup_path']}")
    else:
        print("\nMigration failed!")
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()