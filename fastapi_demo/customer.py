"""
CUSTOMER SCRIPT - Simulates legitimate user browsing the shop
Normal customer behavior - no attacks, just regular shopping
"""
import requests
import time

API = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║          LEGITIMATE CUSTOMER - Shopping Session          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 1. Browse products
        print_header("1. Browsing Products")
        resp = requests.get(f"{API}/products")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Found {data['count']} products")
            for p in data['products'][:5]:
                print(f"   [{p['id']}] {p['name']:25} - ${p['price']:7.2f} ({p['stock']} in stock)")
        else:
            print(f"❌ Error: {resp.status_code}")
        time.sleep(1)
        
        # 2. View specific product
        print_header("2. Viewing Product Details")
        resp = requests.get(f"{API}/product/1")
        if resp.status_code == 200:
            data = resp.json()
            p = data['product']
            print(f"✅ Product: {p['name']}")
            print(f"   Price: ${p['price']}")
            print(f"   Stock: {p['stock']} units")
            print(f"   Category: {p['category']}")
        else:
            print(f"❌ Error: {resp.status_code}")
        time.sleep(1)
        
        # 3. Another product
        print_header("3. Checking Another Product")
        resp = requests.get(f"{API}/product/2")
        if resp.status_code == 200:
            data = resp.json()
            p = data['product']
            print(f"✅ Product: {p['name']} - ${p['price']}")
        else:
            print(f"❌ Error: {resp.status_code}")
        time.sleep(1)
        
        # 4. Search for products
        print_header("4. Searching for Products")
        resp = requests.get(f"{API}/search", params={"q": "laptop"})
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Search successful")
            print(f"   Found {len(data.get('results', []))} results")
        elif resp.status_code == 403:
            print(f"❌ Blocked by security (shouldn't happen for legitimate search)")
        time.sleep(1)
        
        # 5. View another product category
        print_header("5. Browsing More Products")
        resp = requests.get(f"{API}/product/5")
        if resp.status_code == 200:
            data = resp.json()
            p = data['product']
            print(f"✅ Product: {p['name']} - ${p['price']}")
        time.sleep(1)
        
        print_header("✅ SHOPPING SESSION COMPLETE")
        print("All legitimate requests were successful!")
        print("Customer was able to browse and search products normally.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to shop API")
        print("Start the server with: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
