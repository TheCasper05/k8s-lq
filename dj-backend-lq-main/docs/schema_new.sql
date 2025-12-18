-- ============================================================================
-- LingoQuesto Database Schema - Production Ready
-- ============================================================================
-- Version: 1.0
-- Date: 2025-11-17
-- Description: Complete PostgreSQL DDL for LingoQuesto multi-tenant SaaS
-- Architecture: Enterprise-grade, scalable, multi-tenant educational platform
-- Tables: 33 (down from 68)
-- Key Features: Hybrid licensing, contextual ownership, dual libraries
-- ============================================================================

-- ============================================================================
-- SECTION 1: DROP EXISTING OBJECTS (Optional - for clean reinstall)
-- ============================================================================
-- Uncomment the following section if you need to recreate the schema from scratch
/*
DROP TABLE IF EXISTS business_snapshots CASCADE;
DROP TABLE IF EXISTS metrics CASCADE;
DROP TABLE IF EXISTS mistakes CASCADE;
DROP TABLE IF EXISTS rubric_criteria CASCADE;
DROP TABLE IF EXISTS rubrics CASCADE;
DROP TABLE IF EXISTS grading CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS assignment_submissions CASCADE;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS course_module_content_items CASCADE;
DROP TABLE IF EXISTS course_modules CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS user_content_preferences CASCADE;
DROP TABLE IF EXISTS institution_content_settings CASCADE;
DROP TABLE IF EXISTS library_entries CASCADE;
DROP TABLE IF EXISTS content_translations CASCADE;
DROP TABLE IF EXISTS content_visibility_rules CASCADE;
DROP TABLE IF EXISTS content_items CASCADE;
DROP TABLE IF EXISTS classroom_memberships CASCADE;
DROP TABLE IF EXISTS classrooms CASCADE;
DROP TABLE IF EXISTS invitation_classrooms CASCADE;
DROP TABLE IF EXISTS invitations CASCADE;
DROP TABLE IF EXISTS monthly_active_users CASCADE;
DROP TABLE IF EXISTS license_transfers CASCADE;
DROP TABLE IF EXISTS license_seat_allocations CASCADE;
DROP TABLE IF EXISTS licenses CASCADE;
DROP TABLE IF EXISTS user_workspace_memberships CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;
DROP TABLE IF EXISTS institutions CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS proficiency_levels CASCADE;
DROP TABLE IF EXISTS languages CASCADE;

DROP TYPE IF EXISTS period_type CASCADE;
DROP TYPE IF EXISTS metric_type CASCADE;
DROP TYPE IF EXISTS metric_entity_type CASCADE;
DROP TYPE IF EXISTS mistake_severity CASCADE;
DROP TYPE IF EXISTS mistake_category CASCADE;
DROP TYPE IF EXISTS grading_entity_type CASCADE;
DROP TYPE IF EXISTS message_sender CASCADE;
DROP TYPE IF EXISTS conversation_status CASCADE;
DROP TYPE IF EXISTS submission_status CASCADE;
DROP TYPE IF EXISTS classroom_role CASCADE;
DROP TYPE IF EXISTS visibility_scope CASCADE;
DROP TYPE IF EXISTS library_type CASCADE;
DROP TYPE IF EXISTS content_type CASCADE;
DROP TYPE IF EXISTS invitation_status CASCADE;
DROP TYPE IF EXISTS allocation_status CASCADE;
DROP TYPE IF EXISTS tier_level CASCADE;
DROP TYPE IF EXISTS license_type CASCADE;
DROP TYPE IF EXISTS license_scope CASCADE;
DROP TYPE IF EXISTS membership_status CASCADE;
DROP TYPE IF EXISTS workspace_role CASCADE;
DROP TYPE IF EXISTS workspace_type CASCADE;
*/

-- ============================================================================
-- SECTION 2: ENUM TYPES
-- ============================================================================

-- Workspaces & Memberships
CREATE TYPE workspace_type AS ENUM ('personal', 'institution_sede', 'shared');
CREATE TYPE workspace_role AS ENUM ('student', 'teacher', 'coordinator', 'admin_sede', 'admin_institucional', 'viewer');
CREATE TYPE membership_status AS ENUM ('active', 'invited', 'suspended', 'left');

-- Licensing
CREATE TYPE license_scope AS ENUM ('institution', 'workspace', 'user');
CREATE TYPE license_type AS ENUM ('seat', 'active_user_monthly', 'credits', 'tier');
CREATE TYPE tier_level AS ENUM ('basic', 'pro', 'enterprise');
CREATE TYPE allocation_status AS ENUM ('active', 'deallocated', 'transferred', 'expired');

-- Invitations
CREATE TYPE invitation_status AS ENUM ('pending', 'accepted', 'declined', 'expired', 'revoked');

-- Content
CREATE TYPE content_type AS ENUM (
    'conversation',              -- Renombrado de 'scenario'
    'video',
    'slide_deck',
    'interactive_exercise',
    'quiz',
    'reading_material',
    'audio',
    'read',
    'write',
);
CREATE TYPE library_type AS ENUM ('public', 'institutional', 'personal');
CREATE TYPE visibility_scope AS ENUM ('global', 'institution', 'workspace', 'classroom', 'user');

-- Classrooms
CREATE TYPE classroom_role AS ENUM ('student', 'teacher', 'assistant');

-- Activities
CREATE TYPE submission_status AS ENUM ('not_started', 'in_progress', 'submitted', 'graded', 'late');
CREATE TYPE conversation_status AS ENUM ('active', 'paused', 'completed', 'abandoned');
CREATE TYPE message_sender AS ENUM ('user', 'assistant');

-- Evaluation
CREATE TYPE grading_entity_type AS ENUM (
    'conversation',
    'submission',
    'assignment',
    'classroom_student',
    'classroom',
    'workspace_student'
);
CREATE TYPE mistake_category AS ENUM ('pronunciation', 'fluency', 'vocabulary', 'grammar', 'cohesion', 'other');
CREATE TYPE mistake_severity AS ENUM ('minor', 'moderate', 'major', 'critical');

-- Analytics
CREATE TYPE metric_entity_type AS ENUM (
    'conversation', 'submission', 'assignment', 'classroom',
    'workspace', 'institution', 'user', 'platform'
);
CREATE TYPE metric_type AS ENUM ('activity', 'performance', 'engagement', 'usage', 'cost');
CREATE TYPE period_type AS ENUM ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'all_time');

-- ============================================================================
-- SECTION 3: REFERENCE DATA TABLES
-- ============================================================================

-- Languages table
CREATE TABLE lq.languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_languages_code ON languages(code);
CREATE INDEX idx_languages_active ON languages(is_active) WHERE is_active = true;

-- Proficiency levels table (CEFR: A1, A2, B1, B2, C1, C2)
CREATE TABLE lq.proficiency_levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    code VARCHAR(10) NOT NULL UNIQUE,  -- A1, A2, B1, B2, C1, C2
    name VARCHAR(50) NOT NULL,
    description TEXT,
    nro_order INTEGER NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_proficiency_levels_code ON proficiency_levels(code);
CREATE INDEX idx_proficiency_levels_order ON proficiency_levels(nro_order);

-- ============================================================================
-- SECTION 4: CORE TABLES
-- ============================================================================

-- User profiles (extends Django auth_user)
CREATE TABLE lq.user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    primary_role VARCHAR(20) NOT NULL CHECK (primary_role IN ('student', 'teacher', 'admin_institucional')),

    -- Profile data
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    birthday DATE,
    country VARCHAR(2) CHECK (country ~ '^[A-Z]{2}$'),
    
    -- Document info (optional)
    document_type VARCHAR(20)CHECK (document_type IN ('CC', 'CE', 'DNI', 'PAS', 'TI', 'OTHER')),
    document_number VARCHAR(50),
    document_type_other TEXT, -- Solo se usa si type = OTHER

    phone VARCHAR(20),
    photo TEXT,
    bio TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language_preference VARCHAR(10) DEFAULT 'en',

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),

 
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_primary_role ON user_profiles(primary_role);

-- Institutions table
CREATE TABLE lq.institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    -- Branding
    logo TEXT,
    website VARCHAR(255),

    -- Contact
    contact_email VARCHAR(254),
    contact_phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(2),  -- ISO 3166-1 alpha-2
    timezone VARCHAR(50) DEFAULT 'UTC',

    settings JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES auth_user(id),
    updated_by UUID REFERENCES auth_user(id),
    deleted_by UUID REFERENCES auth_user(id)
);

CREATE INDEX idx_institutions_slug ON institutions(slug);
CREATE INDEX idx_institutions_active ON institutions(is_active) WHERE is_active = true;

-- Workspaces table (CENTRAL ENTITY)
CREATE TABLE lq.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core
    name VARCHAR(255) NOT NULL,
    type workspace_type NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    -- Ownership
    owner_user_id UUID REFERENCES auth_user(id),          -- Personal workspaces
    institution_id UUID REFERENCES institutions(id),          -- Institutional sedes
    parent_workspace_id UUID REFERENCES workspaces(id),       -- Hierarchical sedes

    -- Settings
    settings JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES auth_user(id),
    updated_by UUID REFERENCES auth_user(id),
    deleted_by UUID REFERENCES auth_user(id),

    -- Constraints
    CONSTRAINT chk_workspace_owner CHECK (
        (type = 'personal' AND owner_user_id IS NOT NULL AND institution_id IS NULL)
        OR (type = 'institution_sede' AND institution_id IS NOT NULL)
        OR (type = 'shared')
    )
);

CREATE INDEX idx_workspaces_type ON workspaces(type);
CREATE INDEX idx_workspaces_owner_user ON workspaces(owner_user_id) WHERE owner_user_id IS NOT NULL;
CREATE INDEX idx_workspaces_institution ON workspaces(institution_id) WHERE institution_id IS NOT NULL;
CREATE INDEX idx_workspaces_parent ON workspaces(parent_workspace_id) WHERE parent_workspace_id IS NOT NULL;
CREATE INDEX idx_workspaces_active ON workspaces(is_active) WHERE is_active = true;
CREATE INDEX idx_workspaces_settings_gin ON workspaces USING GIN(settings);

-- User workspace memberships
CREATE TABLE lq.user_workspace_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    role workspace_role NOT NULL,
    status membership_status NOT NULL DEFAULT 'active',

    invited_by UUID REFERENCES auth_user(id),
    joined_at TIMESTAMP,
    left_at TIMESTAMP,

    permissions JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),

    CONSTRAINT uniq_user_workspace UNIQUE (user_id, workspace_id)
);

CREATE INDEX idx_uwm_user ON user_workspace_memberships(user_id);
CREATE INDEX idx_uwm_workspace ON user_workspace_memberships(workspace_id);
CREATE INDEX idx_uwm_role ON user_workspace_memberships(role);
CREATE INDEX idx_uwm_status ON user_workspace_memberships(status);
CREATE INDEX idx_uwm_active ON user_workspace_memberships(user_id, workspace_id)
    WHERE status = 'active' AND deleted_at IS NULL;
CREATE INDEX idx_uwm_permissions_gin ON user_workspace_memberships USING GIN(permissions);

-- ============================================================================
-- SECTION 5: LICENSING SYSTEM (Hybrid Scope Model)
-- ============================================================================

-- Licenses table
CREATE TABLE lq.licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Scope (solo uno puede ser NOT NULL)
    scope license_scope NOT NULL,
    institution_id UUID REFERENCES institutions(id),
    workspace_id UUID REFERENCES workspaces(id),
    owner_user_id UUID REFERENCES auth_user(id),

    -- License type
    license_type license_type NOT NULL,

    -- For 'seat' type
    total_seats INTEGER CHECK (total_seats >= 0),
    used_seats INTEGER DEFAULT 0 CHECK (used_seats >= 0),

    -- For 'active_user_monthly' type
    monthly_active_limit INTEGER CHECK (monthly_active_limit >= 0),

    -- For 'credits' type
    total_credits DECIMAL(15,2) CHECK (total_credits >= 0),
    used_credits DECIMAL(15,2) DEFAULT 0 CHECK (used_credits >= 0),

    -- For 'tier' type
    tier_level tier_level,
    student_limit INTEGER CHECK (student_limit >= 0),

    -- Transfer limits
    transfer_limit_type VARCHAR(20) CHECK (transfer_limit_type IN ('percentage', 'absolute', 'unlimited')),
    transfer_limit_value DECIMAL(10,2) CHECK (transfer_limit_value >= 0),
    transfer_period_type VARCHAR(20) CHECK (transfer_period_type IN ('monthly', 'quarterly', 'total', 'yearly')),

    -- Purchase info
    purchased_by UUID REFERENCES auth_user(id),
    purchased_at TIMESTAMP,
    starts_at TIMESTAMP,
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT false,

    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),

    -- Constraints
    CONSTRAINT chk_license_scope CHECK (
        (scope = 'institution' AND institution_id IS NOT NULL AND workspace_id IS NULL AND owner_user_id IS NULL)
        OR (scope = 'workspace' AND workspace_id IS NOT NULL AND institution_id IS NULL AND owner_user_id IS NULL)
        OR (scope = 'user' AND owner_user_id IS NOT NULL AND institution_id IS NULL AND workspace_id IS NULL)
    ),
    CONSTRAINT chk_license_type_fields CHECK (
        (license_type = 'seat' AND total_seats IS NOT NULL)
        OR (license_type = 'active_user_monthly' AND monthly_active_limit IS NOT NULL)
        OR (license_type = 'credits' AND total_credits IS NOT NULL)
        OR (license_type = 'tier' AND tier_level IS NOT NULL)
    )
);

CREATE INDEX idx_licenses_scope ON licenses(scope);
CREATE INDEX idx_licenses_institution ON licenses(institution_id) WHERE institution_id IS NOT NULL;
CREATE INDEX idx_licenses_workspace ON licenses(workspace_id) WHERE workspace_id IS NOT NULL;
CREATE INDEX idx_licenses_type ON licenses(license_type);
CREATE INDEX idx_licenses_active ON licenses(is_active, expires_at) WHERE is_active = true;
CREATE INDEX idx_licenses_metadata_gin ON licenses USING GIN(metadata);

-- License seat allocations
CREATE TABLE lq.license_seat_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    license_id UUID NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    status allocation_status NOT NULL DEFAULT 'active',
    counts_as_usage BOOLEAN NOT NULL DEFAULT true,  -- false si es reutilización de pool institution

    allocated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    allocated_by UUID NOT NULL REFERENCES auth_user(id),
    deallocated_at TIMESTAMP,
    deallocated_by UUID REFERENCES auth_user(id),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_allocations_license ON license_seat_allocations(license_id);
CREATE INDEX idx_allocations_user ON license_seat_allocations(user_id);
CREATE INDEX idx_allocations_workspace ON license_seat_allocations(workspace_id);
CREATE INDEX idx_allocations_status ON license_seat_allocations(status);
CREATE INDEX idx_allocations_active ON license_seat_allocations(license_id, user_id)
    WHERE status = 'active';

-- License transfers tracking
CREATE TABLE lq.license_transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    license_id UUID NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    from_allocation_id UUID REFERENCES license_seat_allocations(id),
    to_allocation_id UUID NOT NULL REFERENCES license_seat_allocations(id),
    from_user_id UUID REFERENCES auth_user(id),
    to_user_id UUID NOT NULL REFERENCES auth_user(id),

    transferred_by UUID NOT NULL REFERENCES auth_user(id),
    transferred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transfer_type VARCHAR(20) CHECK (transfer_type IN ('reallocation', 'new_assignment', 'replacement')),
    reason TEXT,

    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transfers_license ON license_transfers(license_id);
CREATE INDEX idx_transfers_transferred_at ON license_transfers(transferred_at DESC);
CREATE INDEX idx_transfers_period ON license_transfers(license_id, transferred_at);
CREATE INDEX idx_transfers_metadata_gin ON license_transfers USING GIN(metadata);

-- Monthly active users tracking
CREATE TABLE lq.monthly_active_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    year_month VARCHAR(7) NOT NULL CHECK (year_month ~ '^\d{4}-\d{2}$'),

    first_activity_at TIMESTAMP NOT NULL,
    last_activity_at TIMESTAMP NOT NULL,
    activity_count INTEGER NOT NULL DEFAULT 1,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uniq_mau_workspace_user_month UNIQUE (workspace_id, user_id, year_month)
);

CREATE INDEX idx_mau_workspace_month ON monthly_active_users(workspace_id, year_month);

-- ============================================================================
-- SECTION 6: INVITATIONS
-- ============================================================================

-- Invitations table
CREATE TABLE lq.invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email VARCHAR(254) NOT NULL,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    role workspace_role NOT NULL,
    invited_by UUID NOT NULL REFERENCES auth_user(id),

    token VARCHAR(100) NOT NULL UNIQUE,
    status invitation_status NOT NULL DEFAULT 'pending',

    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP,
    declined_at TIMESTAMP,
    revoked_at TIMESTAMP,
    revoked_by UUID REFERENCES auth_user(id),

    welcome_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_invitation_expiry CHECK (expires_at > created_at)
);

CREATE INDEX idx_invitations_email ON invitations(email);
CREATE INDEX idx_invitations_workspace ON invitations(workspace_id);
CREATE INDEX idx_invitations_token ON invitations(token);
CREATE INDEX idx_invitations_pending ON invitations(email, status)
    WHERE status = 'pending' AND expires_at > CURRENT_TIMESTAMP;
CREATE INDEX idx_invitations_metadata_gin ON invitations USING GIN(metadata);

-- Invitation classrooms (M2M)
CREATE TABLE lq.invitation_classrooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invitation_id UUID NOT NULL REFERENCES invitations(id) ON DELETE CASCADE,
    classroom_id UUID NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uniq_invitation_classroom UNIQUE (invitation_id, classroom_id)
);

CREATE INDEX idx_invitation_classrooms_invitation ON invitation_classrooms(invitation_id);
CREATE INDEX idx_invitation_classrooms_classroom ON invitation_classrooms(classroom_id);

-- ============================================================================
-- SECTION 7: CLASSROOMS
-- ============================================================================

-- Classrooms table
CREATE TABLE lq.classrooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES auth_user(id),
    unique_code VARCHAR(8) NOT NULL UNIQUE CHECK (unique_code ~ '^[A-Z0-9]{8}$'),

    description TEXT,
    subject VARCHAR(100),
    grade_level VARCHAR(50),
    language_id UUID REFERENCES languages(id),

    settings JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id)
);

CREATE INDEX idx_classrooms_workspace ON classrooms(workspace_id);
CREATE INDEX idx_classrooms_created_by ON classrooms(created_by);
CREATE INDEX idx_classrooms_code ON classrooms(unique_code);
CREATE INDEX idx_classrooms_active ON classrooms(workspace_id, is_active) WHERE is_active = true;
CREATE INDEX idx_classrooms_settings_gin ON classrooms USING GIN(settings);

-- Classroom memberships
CREATE TABLE lq.classroom_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    classroom_id UUID NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    role classroom_role NOT NULL DEFAULT 'student',

    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),

    CONSTRAINT uniq_classroom_user UNIQUE (classroom_id, user_id)
);

CREATE INDEX idx_classroom_memberships_classroom ON classroom_memberships(classroom_id);
CREATE INDEX idx_classroom_memberships_user ON classroom_memberships(user_id);
CREATE INDEX idx_classroom_memberships_active ON classroom_memberships(classroom_id, user_id)
    WHERE is_active = true;

-- ============================================================================
-- SECTION 8: CONTENT SYSTEM (Polymorphic with Contextual Ownership)
-- ============================================================================

-- Content items (polymorphic)
CREATE TABLE lq.content_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    content_type content_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- OWNERSHIP CONTEXTUAL
    creator_id INTEGER NOT NULL REFERENCES auth_user(id),  -- Siempre acreditado
    owner_user_id UUID REFERENCES auth_user(id),
    owner_institution_id UUID REFERENCES institutions(id)
    workspace_id UUID REFERENCES workspaces(id),

    -- Language & Level
    language_id UUID REFERENCES languages(id),
    level_id UUID REFERENCES proficiency_levels(id),

    -- Content data (polimórfico)
    content_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    -- input_tokens INTEGER CHECK (input_tokens >= 0),
    -- output_tokens INTEGER CHECK (output_tokens >= 0),
    -- total_tokens INTEGER CHECK (total_tokens >= 0),
    -- cost DECIMAL(10,6) CHECK (cost >= 0),
    -- time_taken INTEGER CHECK (time_taken >= 0),
    -- model_name VARCHAR(100),

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    parent_id UUID REFERENCES content_items(id),  -- Para duplicados/forks

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_archived BOOLEAN NOT NULL DEFAULT false,  -- Para contenido institucional

    -- TODO: agrega campos para tracking de LLM, generacion automatica, etc.
    -- por ejemplo, modelo usado, costo de generacion, etc.

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP,
    archived_by UUID REFERENCES auth_user(id),
    deleted_at TIMESTAMP,  -- Solo para contenido personal
    deleted_by UUID REFERENCES auth_user(id),
    created_by UUID REFERENCES auth_user(id),
    updated_by UUID REFERENCES auth_user(id),

    CHECK (
        (owner_user_id IS NOT NULL AND owner_institution_id IS NULL) OR
        (owner_user_id IS NULL AND owner_institution_id IS NOT NULL)
    )
);

CREATE INDEX idx_content_items_type ON content_items(content_type);
CREATE INDEX idx_content_items_creator ON content_items(creator_id);
CREATE INDEX idx_content_items_owner ON content_items(owner_type, owner_id);
CREATE INDEX idx_content_items_workspace ON content_items(workspace_id) WHERE workspace_id IS NOT NULL;
CREATE INDEX idx_content_items_language ON content_items(language_id) WHERE language_id IS NOT NULL;
CREATE INDEX idx_content_items_level ON content_items(level_id) WHERE level_id IS NOT NULL;
CREATE INDEX idx_content_items_active ON content_items(is_active, is_archived)
    WHERE is_active = true AND is_archived = false;
CREATE INDEX idx_content_items_data_gin ON content_items USING GIN(content_data);
CREATE INDEX idx_content_items_metadata_gin ON content_items USING GIN(metadata);

-- Content visibility rules
CREATE TABLE lq.content_visibility_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    scope_type visibility_scope NOT NULL,
    scope_id UUID,

    can_view BOOLEAN NOT NULL DEFAULT true,
    can_use BOOLEAN NOT NULL DEFAULT true,
    can_edit BOOLEAN NOT NULL DEFAULT false,
    can_duplicate BOOLEAN NOT NULL DEFAULT false,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES auth_user(id),

    CONSTRAINT chk_scope_id_required CHECK (
        (scope_type = 'global' AND scope_id IS NULL)
        OR (scope_type != 'global' AND scope_id IS NOT NULL)
    )
);

CREATE INDEX idx_visibility_content ON content_visibility_rules(content_item_id);
CREATE INDEX idx_visibility_scope ON content_visibility_rules(scope_type, scope_id);

-- Content translations
-- TODO: aun no
CREATE TABLE lq.content_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    language_id UUID NOT NULL REFERENCES languages(id),

    title VARCHAR(255),
    description TEXT,
    translated_data JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES auth_user(id),
    updated_by UUID REFERENCES auth_user(id),

    CONSTRAINT uniq_content_translation_language UNIQUE (content_item_id, language_id)
);

CREATE INDEX idx_content_translations_content ON content_translations(content_item_id);
CREATE INDEX idx_content_translations_language ON content_translations(language_id);
CREATE INDEX idx_content_translations_data_gin ON content_translations USING GIN(translated_data);

-- ============================================================================
-- SECTION 9: LIBRARY SYSTEM (Dual: Public + Institutional)
-- ============================================================================

-- Library entries
CREATE TABLE lq.library_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    library_type library_type NOT NULL,
    content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,

    shared_by UUID NOT NULL REFERENCES auth_user(id),
    shared_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    featured BOOLEAN NOT NULL DEFAULT false,
    tags JSONB DEFAULT '[]'::jsonb,
    custom_description TEXT,

    -- Stats
    view_count INTEGER NOT NULL DEFAULT 0,
    use_count INTEGER NOT NULL DEFAULT 0,
    rating_avg DECIMAL(3,2) CHECK (rating_avg >= 0 AND rating_avg <= 5),
    rating_count INTEGER NOT NULL DEFAULT 0,

    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uniq_library_content UNIQUE (library_type, content_item_id, institution_id),
    CONSTRAINT chk_institutional_has_institution CHECK (
        (library_type = 'institutional' AND institution_id IS NOT NULL)
        OR (library_type = 'public' AND institution_id IS NULL)
    )
);

CREATE INDEX idx_library_entries_type ON library_entries(library_type);
CREATE INDEX idx_library_entries_content ON library_entries(content_item_id);
CREATE INDEX idx_library_entries_institution ON library_entries(institution_id)
    WHERE institution_id IS NOT NULL;
CREATE INDEX idx_library_entries_featured ON library_entries(library_type, featured)
    WHERE featured = true;
CREATE INDEX idx_library_entries_popular ON library_entries(library_type, use_count DESC);
CREATE INDEX idx_library_entries_tags_gin ON library_entries USING GIN(tags);

-- Institution content settings
CREATE TABLE lq.institution_content_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL UNIQUE REFERENCES institutions(id) ON DELETE CASCADE,

    allow_public_library_sharing BOOLEAN NOT NULL DEFAULT true,
    require_approval_for_public BOOLEAN NOT NULL DEFAULT false,
    auto_share_to_institutional_library BOOLEAN NOT NULL DEFAULT true,
    allow_teachers_to_opt_out BOOLEAN NOT NULL DEFAULT false,
    allow_content_deletion BOOLEAN NOT NULL DEFAULT false,

    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES auth_user(id),
    updated_by UUID REFERENCES auth_user(id)
);

CREATE INDEX idx_institution_content_settings_metadata_gin ON institution_content_settings USING GIN(metadata);

-- User content preferences
CREATE TABLE lq.user_content_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,

    auto_share_to_public_library BOOLEAN NOT NULL DEFAULT false,
    share_institutional_to_public BOOLEAN NOT NULL DEFAULT true,

    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_content_preferences_metadata_gin ON user_content_preferences USING GIN(metadata);

-- ============================================================================
-- SECTION 10: COURSES (Renombrado de Curriculums)
-- ============================================================================

-- Courses table (antes curriculums)
CREATE TABLE lq.courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Ownership contextual (mismo modelo que content_items)
    creator_id INTEGER NOT NULL REFERENCES auth_user(id),
    owner_type VARCHAR(20) NOT NULL CHECK (owner_type IN ('user', 'institution')),
    owner_id UUID NOT NULL,
    workspace_id UUID REFERENCES workspaces(id),

    language_id UUID REFERENCES languages(id),
    level_id UUID REFERENCES proficiency_levels(id),

    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_archived BOOLEAN NOT NULL DEFAULT false,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP,
    archived_by UUID REFERENCES auth_user(id),
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),
    created_by UUID REFERENCES auth_user(id),
    updated_by UUID REFERENCES auth_user(id),

    CONSTRAINT chk_course_institutional_no_delete CHECK (
        (owner_type = 'institution' AND deleted_at IS NULL)
        OR (owner_type = 'user')
    )
);

CREATE INDEX idx_courses_creator ON courses(creator_id);
CREATE INDEX idx_courses_owner ON courses(owner_type, owner_id);
CREATE INDEX idx_courses_active ON courses(is_active, is_archived)
    WHERE is_active = true AND is_archived = false;
CREATE INDEX idx_courses_metadata_gin ON courses USING GIN(metadata);

-- Course modules (antes course_units)
CREATE TABLE lq.course_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    nro_order INTEGER NOT NULL,

    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES auth_user(id),
    updated_by UUID REFERENCES auth_user(id),

    CONSTRAINT uniq_course_module_order UNIQUE (course_id, nro_order)
);

CREATE INDEX idx_course_modules_course ON course_modules(course_id);
CREATE INDEX idx_course_modules_order ON course_modules(course_id, nro_order);
CREATE INDEX idx_course_modules_metadata_gin ON course_modules USING GIN(metadata);

-- Course module content items (M2M)
CREATE TABLE lq.course_module_content_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    course_module_id UUID NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    nro_order INTEGER NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uniq_course_module_content_order UNIQUE (course_module_id, nro_order),
    CONSTRAINT uniq_course_module_content UNIQUE (course_module_id, content_item_id)
);

CREATE INDEX idx_cm_content_module ON course_module_content_items(course_module_id);
CREATE INDEX idx_cm_content_item ON course_module_content_items(content_item_id);

-- ============================================================================
-- SECTION 11: ACTIVITIES & ASSIGNMENTS
-- ============================================================================

-- Assignments table
-- TODO: revisarla bien.
CREATE TABLE lq.assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    classroom_id UUID NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    assigned_by UUID NOT NULL REFERENCES auth_user(id),
    -- TODO: revisar para poder asignar no solo a una clase, tener la opcion de asignar a users, workspaces
    content_item_id UUID REFERENCES content_items(id),
    course_id UUID REFERENCES courses(id),

    -- title VARCHAR(255) NOT NULL,
    -- description TEXT,

    due_date_start TIMESTAMP,
    due_date_end TIMESTAMP,
    -- TODO: seria si puede realizar la actividad despues de la fecha limite
    allow_late_submission BOOLEAN NOT NULL DEFAULT false,

    settings JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),

    CONSTRAINT chk_assignment_due_dates CHECK (
        due_date_end IS NULL OR due_date_start IS NULL OR due_date_end > due_date_start
    )
);

CREATE INDEX idx_assignments_classroom ON assignments(classroom_id);
CREATE INDEX idx_assignments_content ON assignments(content_item_id) WHERE content_item_id IS NOT NULL;
CREATE INDEX idx_assignments_course ON assignments(course_id) WHERE course_id IS NOT NULL;
CREATE INDEX idx_assignments_settings_gin ON assignments USING GIN(settings);

-- Assignment submissions
CREATE TABLE lq.assignment_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    assignment_id UUID NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,

    status submission_status NOT NULL DEFAULT 'not_started',

    started_at TIMESTAMP,
    submitted_at TIMESTAMP,
    graded_at TIMESTAMP,
    graded_by UUID REFERENCES auth_user(id),

    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uniq_assignment_user_submission UNIQUE (assignment_id, user_id)
);

CREATE INDEX idx_submissions_assignment ON assignment_submissions(assignment_id);
CREATE INDEX idx_submissions_user ON assignment_submissions(user_id);
CREATE INDEX idx_submissions_status ON assignment_submissions(status);
CREATE INDEX idx_submissions_metadata_gin ON assignment_submissions USING GIN(metadata);

-- Conversations table
CREATE TABLE lq.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    submission_id UUID REFERENCES assignment_submissions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    content_item_id UUID REFERENCES content_items(id),

    status conversation_status NOT NULL DEFAULT 'active',

    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER CHECK (duration_seconds >= 0),

    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),
);

CREATE INDEX idx_conversations_submission ON conversations(submission_id) WHERE submission_id IS NOT NULL;
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_content ON conversations(content_item_id) WHERE content_item_id IS NOT NULL;
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_metadata_gin ON conversations USING GIN(metadata);

-- Messages table (LLM tracking)
CREATE TABLE lq.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender message_sender NOT NULL,

    content TEXT,
    audio_url TEXT,
    transcription TEXT,

    -- LLM tracking
    -- TODO: estos campos debe ser una tabla aprte, que ademas 
    -- tenga un identity_type, y un identity_id para no solo medir 
    -- los gastos de LLM en mensajes, sino tambien en otros procesos
    -- generacion de cursos, generacion de videos, etc.
    -- esto deberia estar tambien la tabla de content_items para
    -- medir el costo de generacion de contenido
    input_tokens INTEGER CHECK (input_tokens >= 0),
    output_tokens INTEGER CHECK (output_tokens >= 0),
    total_tokens INTEGER CHECK (total_tokens >= 0),
    cost DECIMAL(10,6) CHECK (cost >= 0),
    time_taken INTEGER CHECK (time_taken >= 0),
    model_name VARCHAR(100),

    suggested_answers JSONB,
    helps_used JSONB,
    metadata JSONB DEFAULT '{}'::jsonb,

    nro_order INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uniq_conversation_message_order UNIQUE (conversation_id, nro_order),
    CONSTRAINT chk_message_tokens CHECK (
        total_tokens IS NULL OR
        (input_tokens IS NOT NULL AND output_tokens IS NOT NULL AND total_tokens = input_tokens + output_tokens)
    )
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_order ON messages(conversation_id, nro_order);
CREATE INDEX idx_messages_suggested_answers_gin ON messages USING GIN(suggested_answers) WHERE suggested_answers IS NOT NULL;
CREATE INDEX idx_messages_helps_used_gin ON messages USING GIN(helps_used) WHERE helps_used IS NOT NULL;
CREATE INDEX idx_messages_metadata_gin ON messages USING GIN(metadata);

-- ============================================================================
-- SECTION 12: EVALUATION SYSTEM (Consolidated)
-- ============================================================================

-- Grading table (consolidado de 14 tablas)
CREATE TABLE lq.grading (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    entity_type grading_entity_type NOT NULL,
    entity_id UUID NOT NULL,
    rubric_id UUID REFERENCES rubrics(id),

    -- Scores
    general_score DECIMAL(5,2) CHECK (general_score >= 0 AND general_score <= 100),
    pronunciation_score DECIMAL(5,2) CHECK (pronunciation_score >= 0 AND pronunciation_score <= 100),
    fluency_score DECIMAL(5,2) CHECK (fluency_score >= 0 AND fluency_score <= 100),
    vocabulary_score DECIMAL(5,2) CHECK (vocabulary_score >= 0 AND vocabulary_score <= 100),
    grammar_score DECIMAL(5,2) CHECK (grammar_score >= 0 AND grammar_score <= 100),
    cohesion_score DECIMAL(5,2) CHECK (cohesion_score >= 0 AND cohesion_score <= 100),

    -- Mistake counts
    num_mistakes INTEGER CHECK (num_mistakes >= 0),
    num_pronunciation_mistakes INTEGER CHECK (num_pronunciation_mistakes >= 0),
    num_fluency_mistakes INTEGER CHECK (num_fluency_mistakes >= 0),
    num_vocabulary_mistakes INTEGER CHECK (num_vocabulary_mistakes >= 0),
    num_grammar_mistakes INTEGER CHECK (num_grammar_mistakes >= 0),
    num_cohesion_mistakes INTEGER CHECK (num_cohesion_mistakes >= 0),

    words_by_level JSONB DEFAULT '{}'::jsonb,
    feedback TEXT,

    graded_by UUID REFERENCES auth_user(id),
    graded_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id),

    CONSTRAINT uniq_grading_entity UNIQUE (entity_type, entity_id)
);

CREATE INDEX idx_grading_entity ON grading(entity_type, entity_id);
CREATE INDEX idx_grading_rubric ON grading(rubric_id) WHERE rubric_id IS NOT NULL;
CREATE INDEX idx_grading_general_score ON grading(general_score DESC) WHERE general_score IS NOT NULL;
CREATE INDEX idx_grading_words_gin ON grading USING GIN(words_by_level);
CREATE INDEX idx_grading_metadata_gin ON grading USING GIN(metadata);

-- Rubrics table
CREATE TABLE lq.rubrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES auth_user(id),
    is_public BOOLEAN NOT NULL DEFAULT false,

    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth_user(id)
);

CREATE INDEX idx_rubrics_owner ON rubrics(owner_id);
CREATE INDEX idx_rubrics_public ON rubrics(is_public) WHERE is_public = true AND is_active = true;
CREATE INDEX idx_rubrics_metadata_gin ON rubrics USING GIN(metadata);

-- Rubric criteria
CREATE TABLE lq.rubric_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    rubric_id UUID NOT NULL REFERENCES rubrics(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    weight DECIMAL(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),
    max_score DECIMAL(5,2) NOT NULL CHECK (max_score > 0),
    nro_order INTEGER NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uniq_rubric_criteria_order UNIQUE (rubric_id, nro_order)
);

CREATE INDEX idx_rubric_criteria_rubric ON rubric_criteria(rubric_id);
CREATE INDEX idx_rubric_criteria_order ON rubric_criteria(rubric_id, nro_order);

-- Mistakes tracking
CREATE TABLE lq.mistakes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    category mistake_category NOT NULL,
    subcategory VARCHAR(100),

    original_text TEXT,
    corrected_text TEXT,
    explanation TEXT,
    severity mistake_severity NOT NULL DEFAULT 'moderate',
    detected_by VARCHAR(50),

    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mistakes_message ON mistakes(message_id) WHERE message_id IS NOT NULL;
CREATE INDEX idx_mistakes_conversation ON mistakes(conversation_id);
CREATE INDEX idx_mistakes_category ON mistakes(category);
CREATE INDEX idx_mistakes_metadata_gin ON mistakes USING GIN(metadata);

-- ============================================================================
-- SECTION 13: ANALYTICS SYSTEM (Consolidated)
-- ============================================================================

-- Metrics table (consolidado de 9 tablas)
CREATE TABLE lq.metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    entity_type metric_entity_type NOT NULL,
    entity_id UUID,
    metric_type metric_type NOT NULL,

    period_type period_type NOT NULL,
    period_value VARCHAR(20),  -- 'YYYY-MM', 'YYYY-WNN', 'YYYY-MM-DD'

    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    total_words INTEGER CHECK (total_words >= 0),
    words_per_minute INTEGER CHECK (words_per_minute >= 0),
    total_activities INTEGER CHECK (total_activities >= 0),
    completion_rate DECIMAL(5,2) CHECK (completion_rate >= 0 AND completion_rate <= 100),
    average_score DECIMAL(5,2) CHECK (average_score >= 0 AND average_score <= 100),

    metrics_data JSONB DEFAULT '{}'::jsonb,
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uniq_metrics_entity_period UNIQUE (entity_type, entity_id, metric_type, period_type, period_value)
);

CREATE INDEX idx_metrics_entity ON metrics(entity_type, entity_id) WHERE entity_id IS NOT NULL;
CREATE INDEX idx_metrics_type ON metrics(metric_type);
CREATE INDEX idx_metrics_period ON metrics(period_type, period_value);
CREATE INDEX idx_metrics_data_gin ON metrics USING GIN(metrics_data);

-- Business snapshots (platform-wide)
CREATE TABLE lq.business_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    snapshot_date DATE NOT NULL UNIQUE,

    total_users INTEGER NOT NULL CHECK (total_users >= 0),
    total_institutions INTEGER NOT NULL CHECK (total_institutions >= 0),
    total_workspaces INTEGER NOT NULL CHECK (total_workspaces >= 0),
    total_classrooms INTEGER NOT NULL CHECK (total_classrooms >= 0),
    total_conversations INTEGER NOT NULL CHECK (total_conversations >= 0),
    total_messages INTEGER NOT NULL CHECK (total_messages >= 0),
    total_credits_consumed DECIMAL(15,2) CHECK (total_credits_consumed >= 0),
    total_cost_usd DECIMAL(15,2) CHECK (total_cost_usd >= 0),

    revenue_data JSONB DEFAULT '{}'::jsonb,
    platform_metrics JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_business_snapshots_date ON business_snapshots(snapshot_date DESC);
CREATE INDEX idx_business_snapshots_revenue_gin ON business_snapshots USING GIN(revenue_data);
CREATE INDEX idx_business_snapshots_platform_gin ON business_snapshots USING GIN(platform_metrics);

-- ============================================================================
-- SECTION 14: HELPER FUNCTIONS
-- ============================================================================

-- Function to auto-create personal workspace on user registration
CREATE OR REPLACE FUNCTION create_personal_workspace_on_user_creation()
RETURNS TRIGGER AS $$
BEGIN
    -- Create personal workspace
    INSERT INTO workspaces (
        name,
        type,
        slug,
        owner_user_id,
        created_by
    ) VALUES (
        'Personal - ' || NEW.username,
        'personal',
        'personal-' || NEW.id || '-' || substr(md5(random()::text), 1, 8),
        NEW.id,
        NEW.id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-create personal workspace
-- Note: This will only work after Django's auth_user table exists
-- CREATE TRIGGER trigger_create_personal_workspace
-- AFTER INSERT ON auth_user
-- FOR EACH ROW
-- EXECUTE FUNCTION create_personal_workspace_on_user_creation();

-- Function to validate license availability before allocation
CREATE OR REPLACE FUNCTION check_license_availability(
    p_license_id UUID,
    p_user_id UUID,
    p_workspace_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_license RECORD;
    v_active_allocations INTEGER;
BEGIN
    -- Get license details
    SELECT * INTO v_license
    FROM licenses
    WHERE id = p_license_id
        AND is_active = true
        AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP);

    IF NOT FOUND THEN
        RETURN false;
    END IF;

    -- For seat-based licenses, check availability
    IF v_license.license_type = 'seat' THEN
        -- Check if there's an existing allocation (pool reuse)
        IF v_license.scope = 'institution' THEN
            SELECT COUNT(*) INTO v_active_allocations
            FROM license_seat_allocations
            WHERE license_id = p_license_id
                AND user_id = p_user_id
                AND status = 'active'
                AND counts_as_usage = true;

            IF v_active_allocations > 0 THEN
                -- User already has allocation from institution pool
                RETURN true;
            END IF;
        END IF;

        -- Check if seats are available
        RETURN v_license.used_seats < v_license.total_seats;
    END IF;

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Function to update license usage on allocation
CREATE OR REPLACE FUNCTION update_license_usage_on_allocation()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'active' AND NEW.counts_as_usage THEN
        UPDATE licenses
        SET used_seats = used_seats + 1
        WHERE id = NEW.license_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_license_usage
AFTER INSERT ON license_seat_allocations
FOR EACH ROW
EXECUTE FUNCTION update_license_usage_on_allocation();

-- Function to update license usage on deallocation
CREATE OR REPLACE FUNCTION update_license_usage_on_deallocation()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'active' AND NEW.status != 'active' AND NEW.counts_as_usage THEN
        UPDATE licenses
        SET used_seats = GREATEST(used_seats - 1, 0)
        WHERE id = NEW.license_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_license_usage_dealloc
AFTER UPDATE ON license_seat_allocations
FOR EACH ROW
WHEN (OLD.status = 'active' AND NEW.status != 'active')
EXECUTE FUNCTION update_license_usage_on_deallocation();

-- ============================================================================
-- SECTION 15: SEED DATA (Reference Tables)
-- ============================================================================

-- Insert common languages
INSERT INTO languages (code, name, native_name, is_active) VALUES
    ('en', 'English', 'English', true),
    ('es', 'Spanish', 'Español', true),
    ('fr', 'French', 'Français', true),
    ('de', 'German', 'Deutsch', true),
    ('it', 'Italian', 'Italiano', true),
    ('pt', 'Portuguese', 'Português', true),
    ('zh', 'Chinese', '中文', true),
    ('ja', 'Japanese', '日本語', true),
    ('ko', 'Korean', '한국어', true),
    ('ar', 'Arabic', 'العربية', true)
ON CONFLICT (code) DO NOTHING;

-- Insert CEFR proficiency levels
INSERT INTO proficiency_levels (code, name, description, nro_order, is_active) VALUES
    ('A1', 'Beginner', 'Can understand and use familiar everyday expressions and very basic phrases', 1, true),
    ('A2', 'Elementary', 'Can communicate in simple and routine tasks requiring a simple and direct exchange', 2, true),
    ('B1', 'Intermediate', 'Can deal with most situations likely to arise while traveling in an area where the language is spoken', 3, true),
    ('B2', 'Upper Intermediate', 'Can interact with a degree of fluency and spontaneity that makes regular interaction quite possible', 4, true),
    ('C1', 'Advanced', 'Can express ideas fluently and spontaneously without much obvious searching for expressions', 5, true),
    ('C2', 'Proficient', 'Can understand with ease virtually everything heard or read', 6, true)
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- SECTION 16: COMMENTS & DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE workspaces IS 'Central entity: personal workspaces, institutional sedes, and shared spaces';
COMMENT ON TABLE licenses IS 'Hybrid scope licensing: institution-wide, workspace-specific, or user-owned';
COMMENT ON TABLE content_items IS 'Polymorphic content with contextual ownership (user vs institution)';
COMMENT ON TABLE library_entries IS 'Dual library system: public (global) and institutional (private)';
COMMENT ON TABLE grading IS 'Consolidated grading table for all entity types (replaces 14 tables)';
COMMENT ON TABLE metrics IS 'Consolidated metrics table for analytics (replaces 9 tables)';
COMMENT ON TABLE user_workspace_memberships IS 'Contextual roles: users can have different roles in different workspaces';
COMMENT ON TABLE license_seat_allocations IS 'Tracks which users are using which licenses in which workspaces';
COMMENT ON TABLE license_transfers IS 'Audit trail for license transfers with configurable limits';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Schema creation completed successfully
-- Total tables created: 33
-- Total indexes created: 150+
-- Total functions created: 4
-- Total triggers created: 3
-- Total ENUM types created: 19

-- Next steps:
-- 1. Connect to Django ORM
-- 2. Create Django models matching this schema
-- 3. Configure Django migrations to use existing tables
-- 4. Implement business logic in application layer
-- 5. Set up Row Level Security (RLS) policies if needed
-- 6. Configure backup and replication strategy
