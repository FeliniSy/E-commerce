CREATE TABLE field_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    parent_id INT,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    image_url VARCHAR(2048),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_category_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE NO ACTION
);

CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    logo_url VARCHAR(2048),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    supplier_type VARCHAR(50) NOT NULL CHECK (supplier_type IN ('external', 'internal')),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL, -- Removed unique here because of the group constraint
    group_id INT,
    CONSTRAINT fk_fields_group FOREIGN KEY (group_id) REFERENCES field_groups(id) ON DELETE SET NULL,
    CONSTRAINT uq_field_name_group UNIQUE (name, group_id)
);

CREATE TABLE category_fields (
    id SERIAL PRIMARY KEY,
    category_id INT NOT NULL,
    field_id INT NOT NULL,
    is_required BOOLEAN DEFAULT FALSE,
    CONSTRAINT uq_category_field UNIQUE (category_id, field_id),
    CONSTRAINT fk_category_fields_cat FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    CONSTRAINT fk_category_fields_field FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

CREATE TABLE field_options (
    id SERIAL PRIMARY KEY,
    field_id INT NOT NULL,
    value TEXT NOT NULL, -- Updated from VARCHAR to TEXT per your alter
    CONSTRAINT fk_field_options_field FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INT NOT NULL,
    supplier_id INT NOT NULL,
    brand_id INT NOT NULL,
    cover_image_url VARCHAR(500), -- Updated type per your alter
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CONSTRAINT chk_price_positive CHECK (price >= 0),
    cost_price DECIMAL(10,2) NOT NULL DEFAULT 0 CONSTRAINT chk_cost_positive CHECK (cost_price >= 0),
    sku VARCHAR(500) UNIQUE NOT NULL, -- Updated length per your alter
    stock_quantity INT NOT NULL DEFAULT 0,
    original_url VARCHAR(2048),
    sell_type VARCHAR(150), -- Added per your alter
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_cat FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE NO ACTION,
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE NO ACTION,
    CONSTRAINT fk_products_brand FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE NO ACTION
    -- Note: fk_products_cover_image was dropped in your alter commands
);

CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(2048) NOT NULL,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_images_prod FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT uq_product_image UNIQUE (product_id, image_url)
);

CREATE TABLE product_field_values (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    field_id INT NOT NULL,
    option_id INT NOT NULL,
    CONSTRAINT uq_product_field UNIQUE (product_id, field_id),
    CONSTRAINT fk_pfv_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_pfv_field FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE NO ACTION,
    CONSTRAINT fk_pfv_option FOREIGN KEY (option_id) REFERENCES field_options(id) ON DELETE NO ACTION
);

CREATE TABLE product_addresses (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    branch_name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    full_address TEXT NOT NULL,
    phone_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_product_branch UNIQUE (product_id, branch_name),
    CONSTRAINT fk_address_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE external_scrapers (
    supplier_id INT PRIMARY KEY,
    website_url VARCHAR(2048) NOT NULL,
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    CONSTRAINT fk_scraper_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

CREATE TABLE platform_sellers (
    supplier_id INT PRIMARY KEY,
    user_id UUID NOT NULL,
    identification_number VARCHAR(50) NOT NULL,
    legal_address VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    bank_account_number VARCHAR(50),
    CONSTRAINT fk_seller_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
    CONSTRAINT fk_seller_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE NO ACTION
);

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE,
    name VARCHAR(255),
    surname VARCHAR(255),
    phone_number VARCHAR(50) UNIQUE,
    birth_date DATE,
    avatar_url TEXT,
    location VARCHAR(255),
    bio TEXT,
    gender BOOLEAN,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE listing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    swap_item_title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_listing_profile FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE TABLE listing_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL,
    photo_url TEXT NOT NULL,
    CONSTRAINT fk_listing FOREIGN KEY (listing_id) REFERENCES listing(id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id INT NOT NULL,
    quantity SMALLINT DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cart_item_user_product UNIQUE (user_id, product_id),
    CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE wishlist_items (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_wishlist_item_user_product UNIQUE (user_id, product_id),
    CONSTRAINT fk_wishlist_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_wishlist_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

select * from categories

insert into categories(parent_id, name, slug, image_url )
			values(null, 'ტექნიკა', 'teqnika', 'https://storage.googleapis.com/vipo-images/category_images/%E1%83%A2%E1%83%94%E1%83%A5%E1%83%9C%E1%83%98%E1%83%99%E1%83%90.png')

INSERT INTO suppliers (name, supplier_type) values ('alta', 'external')

insert into external_scrapers(supplier_id,website_url,contact_phone,contact_email)
values (1,'https://alta.ge/','(032) 238-00-38','retail@alta.ge')
update categories set parent_id = 5 where id in (2,3,4)