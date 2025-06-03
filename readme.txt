-- 1. Create the 'roles' table
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create the 'users' table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role_id
        FOREIGN KEY (role_id)
        REFERENCES roles (role_id)
        ON DELETE RESTRICT
);

-- 3. Create the 'projects' table
CREATE TABLE projects (
    project_id VARCHAR(50) PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create the 'journal_entries' table
CREATE TABLE journal_entries (
    journal_entry_id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL,
    description TEXT,
    source_system TEXT,
    source_reference_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create the 'invoices' table
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    vendor_id VARCHAR(255) NOT NULL,
    amount NUMERIC(19, 4) NOT NULL,
    expense_account_code TEXT,
    payable_account_code TEXT,
    project_id VARCHAR(50),
    status TEXT NOT NULL DEFAULT 'Draft',
    created_by_user_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_invoices_project_id
        FOREIGN KEY (project_id)
        REFERENCES projects (project_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_invoices_created_by_user_id
        FOREIGN KEY (created_by_user_id)
        REFERENCES users (user_id)
        ON DELETE SET NULL
);

-- 6. Create the 'ledger_transactions' table
CREATE TABLE ledger_transactions (
    ledger_transaction_id SERIAL PRIMARY KEY,
    journal_entry_id INTEGER NOT NULL,
    account_code TEXT NOT NULL,
    debit_amount NUMERIC(19, 4) DEFAULT 0,
    credit_amount NUMERIC(19, 4) DEFAULT 0,
    project_id VARCHAR(50),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ledger_transactions_journal_entry_id
        FOREIGN KEY (journal_entry_id)
        REFERENCES journal_entries (journal_entry_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ledger_transactions_project_id
        FOREIGN KEY (project_id)
        REFERENCES projects (project_id)
        ON DELETE SET NULL
);

-- Optional: Insert default roles
INSERT INTO roles (name) VALUES ('Admin'), ('Accountant'), ('User')
ON CONFLICT (name) DO NOTHING;

-- To verify tables:
-- \dt
-- To inspect schema:
-- \d+ table_name
