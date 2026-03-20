select_category = """
                  SELECT id
                  FROM categories
                  WHERE name = %s \
                  """

insert_category = """
                  INSERT INTO categories (name, parent_id, slug, image_url)
                  VALUES (%s, %s, %s, %s) ON CONFLICT (slug) DO
                  UPDATE SET
                      image_url = COALESCE (EXCLUDED.image_url, categories.image_url) \
                  """

select_brand = "SELECT id FROM brands WHERE name = %s"
insert_brand = """
               INSERT INTO brands (name)
               VALUES (%s) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
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
insert_option = """
                INSERT INTO field_options (field_id, value)
                VALUES (%s, %s)
                ON CONFLICT (field_id, value) DO NOTHING
                """

insert_pfv = """
             INSERT INTO product_field_values (product_id, field_id, option_id)
             VALUES (%s, %s, %s) ON CONFLICT (product_id, field_id)
             DO UPDATE SET option_id = EXCLUDED.option_id \
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
                                       price, cost_price, sku, stock_quantity, original_url, sell_type, is_scrapped)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s) ON CONFLICT (original_url)
                 DO UPDATE SET
                     category_id = EXCLUDED.category_id,
                     brand_id = EXCLUDED.brand_id,
                     cover_image_url = EXCLUDED.cover_image_url,
                     title = EXCLUDED.title,
                     description = EXCLUDED.description,
                     price = EXCLUDED.price,
                     cost_price = EXCLUDED.cost_price,
                     sku = EXCLUDED.sku,
                     stock_quantity = EXCLUDED.stock_quantity,
                     sell_type = EXCLUDED.sell_type,
                     updated_at = CURRENT_TIMESTAMP
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

# Get fields and field_groups for a specific category
select_fields_by_category = """
                            SELECT
                                fg.id as group_id,
                                fg.name as group_name,
                                f.id as field_id,
                                f.name as field_name,
                                cf.is_required
                            FROM category_fields cf
                            JOIN fields f ON cf.field_id = f.id
                            JOIN field_groups fg ON f.group_id = fg.id
                            WHERE cf.category_id = %s
                            ORDER BY fg.name, f.name \
                            """

# Get field options for fields belonging to a specific category
select_field_options_by_category = """
                                   SELECT
                                       f.id as field_id,
                                       f.name as field_name,
                                       fo.id as option_id,
                                       fo.value as option_value
                                   FROM category_fields cf
                                   JOIN fields f ON cf.field_id = f.id
                                   JOIN field_options fo ON f.id = fo.field_id
                                   WHERE cf.category_id = %s
                                   ORDER BY f.name, fo.value \
                                   """
