from auth import register, login

# 👇 Ye sirf ek baar chalana
register("Prajwla", "test@mail.com", "1234")

# 👇 Login test
user = login("test@mail.com", "1234")

if user:
    print("✅ Login success")
    print("User ID:", user[0])
    print("Name:", user[1])
else:
    print("❌ Login failed")
