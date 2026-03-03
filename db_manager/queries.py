select_category = """
                  SELECT id
                  FROM categories
                  WHERE name = %s \
                  """

insert_category = """
                  INSERT INTO categories (name, parent_id, slug, image_url)
                  VALUES (%s, %s, %s, %s) ON CONFLICT (slug) DO NOTHING \
                  """

select_brand = "SELECT id FROM brands WHERE name = %s"
insert_brand = """
               INSERT INTO brands (name)
               VALUES (%s) ON CONFLICT (name) DO NOTHING
    RETURNING id \
               """

select_field_group = "SELECT id FROM field_groups WHERE name = %s"
insert_field_group = "INSERT INTO field_groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING"

select_field = "SELECT id FROM fields WHERE name = %s AND group_id = %s"
insert_field = """
               INSERT INTO fields (name, group_id)
               VALUES (%s, %s) ON CONFLICT (name, group_id) DO NOTHING \
               """

select_option = "SELECT id FROM field_options WHERE field_id = %s AND value = %s"
insert_option = "INSERT INTO field_options (field_id, value) VALUES (%s, %s)"

insert_pfv = """
             INSERT INTO product_field_values (product_id, field_id, option_id)
             VALUES (%s, %s, %s) ON CONFLICT (product_id, field_id) DO NOTHING \
             """

select_category_field = """
                        SELECT id
                        FROM category_fields
                        WHERE category_id = %s
                          AND field_id = %s \
                        """

insert_category_field = """
                        INSERT INTO category_fields (category_id, field_id, is_required)
                        VALUES (%s, %s, %s) ON CONFLICT (category_id, field_id) DO NOTHING \
                        """

insert_supplier = """
                  INSERT INTO suppliers (name, supplier_type)
                  VALUES (%s, %s) ON CONFLICT DO NOTHING \
                  """

insert_external_supplier = """
                           INSERT INTO external_scrapers (supplier_id, website_url, contact_phone, contact_email)
                           VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING \
                           """

insert_product = """
                 INSERT INTO products (category_id, supplier_id, brand_id, cover_image_url, title, description,
                                       price, cost_price, sku, stock_quantity, original_url, sell_type)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (original_url) 
                 DO NOTHING
                RETURNING id \
                 """

select_product = "SELECT id FROM products WHERE original_url = %s"

insert_product_image = """
                       INSERT INTO product_images (product_id, image_url)
                       VALUES (%s, %s) ON CONFLICT DO NOTHING \
                       """

insert_product_address = """
                         INSERT INTO product_addresses (product_id, branch_name, country, city, full_address, phone_number)
                         VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (product_id, branch_name) DO NOTHING \
                         """
