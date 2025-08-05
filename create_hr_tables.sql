BEGIN;
--
-- Create model Employee
--
CREATE TABLE "employees_employee" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "email" varchar(254) NOT NULL UNIQUE, "department" varchar(20) NOT NULL, "position" varchar(20) NOT NULL, "hire_date" date NOT NULL, "phone" varchar(15) NOT NULL, "address" text NOT NULL, "emergency_contact" varchar(50) NOT NULL, "emergency_phone" varchar(15) NOT NULL, "profile_image" varchar(100) NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "job_group" varchar(20) NOT NULL, "job_type" varchar(50) NOT NULL, "job_role" varchar(100) NOT NULL, "growth_level" integer NOT NULL, "new_position" varchar(50) NOT NULL, "grade_level" integer NOT NULL, "employment_type" varchar(20) NOT NULL, "employment_status" varchar(20) NOT NULL, "manager_id" bigint NULL REFERENCES "employees_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model HRContractor
--
CREATE TABLE "hr_contractors" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "contractor_name" varchar(100) NOT NULL, "vendor_company" varchar(200) NOT NULL, "project_name" varchar(200) NOT NULL, "department" varchar(100) NULL, "role" varchar(100) NULL, "start_date" date NULL, "end_date" date NULL, "daily_rate" decimal NULL, "monthly_rate" decimal NULL, "status" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model HREmployee
--
CREATE TABLE "hr_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "employee_no" varchar(20) NULL UNIQUE, "name" varchar(100) NOT NULL, "company" varchar(100) NOT NULL, "department" varchar(100) NULL, "position" varchar(50) NULL, "job_level" varchar(50) NULL, "location_type" varchar(20) NOT NULL, "country" varchar(50) NULL, "branch" varchar(100) NULL, "employment_type" varchar(20) NOT NULL, "hire_date" date NULL, "resignation_date" date NULL, "status" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model HRFileUpload
--
CREATE TABLE "hr_file_uploads" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "file_name" varchar(255) NOT NULL, "file_type" varchar(50) NOT NULL, "report_date" date NOT NULL, "upload_date" datetime NOT NULL, "processed_status" varchar(20) NOT NULL, "total_records" integer NULL, "success_records" integer NULL, "error_records" integer NULL, "error_log" text NULL, "uploaded_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model HRMonthlySnapshot
--
CREATE TABLE "hr_monthly_snapshots" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "snapshot_date" date NOT NULL, "company" varchar(100) NOT NULL, "department" varchar(100) NULL, "position" varchar(50) NULL, "job_level" varchar(50) NULL, "location_type" varchar(20) NOT NULL, "country" varchar(50) NULL, "created_at" datetime NOT NULL, "employee_id" bigint NOT NULL REFERENCES "hr_employees" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "employees_employee_manager_id_2f52c91e" ON "employees_employee" ("manager_id");
CREATE INDEX "hr_contract_vendor__b40412_idx" ON "hr_contractors" ("vendor_company");
CREATE INDEX "hr_contract_project_05a6b3_idx" ON "hr_contractors" ("project_name");
CREATE INDEX "hr_contract_status_fc8cb1_idx" ON "hr_contractors" ("status");
CREATE INDEX "hr_employee_name_e4a113_idx" ON "hr_employees" ("name");
CREATE INDEX "hr_employee_company_2a55aa_idx" ON "hr_employees" ("company");
CREATE INDEX "hr_employee_status_ad4954_idx" ON "hr_employees" ("status");
CREATE INDEX "hr_file_uploads_uploaded_by_id_dace38df" ON "hr_file_uploads" ("uploaded_by_id");
CREATE UNIQUE INDEX "hr_monthly_snapshots_snapshot_date_employee_id_66dd54ae_uniq" ON "hr_monthly_snapshots" ("snapshot_date", "employee_id");
CREATE INDEX "hr_monthly_snapshots_employee_id_c1ebe5d9" ON "hr_monthly_snapshots" ("employee_id");
CREATE INDEX "hr_monthly__snapsho_14bc80_idx" ON "hr_monthly_snapshots" ("snapshot_date");
COMMIT;
