
# params (email, password, display_name, registration_utc)
CREATE_NEW_USER = """
INSERT INTO users
(email, password, display_name, registration_utc)
VALUES
($1, $2, $3, $4)
RETURNING 
(id);
"""

# params (id, email, password, display_name, registration_utc, avatar, description)
UPDATE_USER = """
UPDATE users 
SET
email = $2, password = $3, display_name = $4, registration_utc = $5, avatar = $6, description = $7
WHERE id = $1;
"""

# params (id)
# return (email, password, display_name, registration_utc, avatar, description)
USER_META = """
SELECT *
FROM users
WHERE id = $1;
"""