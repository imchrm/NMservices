#!/usr/bin/env python3
"""
Test script for Admin API endpoints.

Tests all admin functionality remotely via HTTP API.
"""

import asyncio
import sys
from typing import Optional
import httpx
from decimal import Decimal


class AdminAPITester:
    """Admin API testing client."""

    def __init__(self, base_url: str, admin_key: str):
        """
        Initialize the tester.

        Args:
            base_url: Base URL of the API (e.g., http://localhost:8000)
            admin_key: Admin secret key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "X-Admin-Key": admin_key,
            "Content-Type": "application/json"
        }
        self.test_user_id: Optional[int] = None
        self.test_order_id: Optional[int] = None

    async def run_all_tests(self):
        """Run all admin API tests."""
        print("=" * 60)
        print("🧪 TESTING ADMIN API")
        print("=" * 60)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Admin Key: {'*' * (len(self.headers['X-Admin-Key']) - 4) + self.headers['X-Admin-Key'][-4:]}")
        print("=" * 60)

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test sequence
            tests = [
                ("Health Check", self.test_health_check),
                ("Statistics (Initial)", self.test_statistics),
                ("List Users (Empty)", self.test_list_users),
                ("Create User", self.test_create_user),
                ("Get User by ID", self.test_get_user),
                ("List Users (With Data)", self.test_list_users),
                ("Create Order", self.test_create_order),
                ("Get Order by ID", self.test_get_order),
                ("List Orders", self.test_list_orders),
                ("Get User's Orders", self.test_get_user_orders),
                ("Update Order", self.test_update_order),
                ("List Orders with Filter", self.test_list_orders_filtered),
                ("Statistics (Final)", self.test_statistics),
                ("Delete Order", self.test_delete_order),
                ("Delete User", self.test_delete_user),
                ("Verify Deletion", self.test_verify_deletion),
            ]

            passed = 0
            failed = 0

            for test_name, test_func in tests:
                try:
                    print(f"\n📝 {test_name}...", end=" ")
                    await test_func(client)
                    print("✅ PASSED")
                    passed += 1
                except Exception as e:
                    print(f"❌ FAILED: {e}")
                    failed += 1

            print("\n" + "=" * 60)
            print(f"📊 RESULTS: {passed} passed, {failed} failed")
            print("=" * 60)

            return failed == 0

    async def test_health_check(self, client: httpx.AsyncClient):
        """Test root health check endpoint."""
        response = await client.get(f"{self.base_url}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data, "Response missing 'message' field"

    async def test_statistics(self, client: httpx.AsyncClient):
        """Test statistics endpoint."""
        response = await client.get(
            f"{self.base_url}/admin/stats",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "total_users" in data, "Missing total_users"
        assert "total_orders" in data, "Missing total_orders"
        assert "orders_by_status" in data, "Missing orders_by_status"
        print(f"(Users: {data['total_users']}, Orders: {data['total_orders']})", end=" ")

    async def test_list_users(self, client: httpx.AsyncClient):
        """Test listing users."""
        response = await client.get(
            f"{self.base_url}/admin/users",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "users" in data, "Missing users field"
        assert "total" in data, "Missing total field"
        print(f"(Found {data['total']} users)", end=" ")

    async def test_create_user(self, client: httpx.AsyncClient):
        """Test creating a user."""
        phone = f"+998901234567"
        response = await client.post(
            f"{self.base_url}/admin/users",
            headers=self.headers,
            json={"phone_number": phone}
        )

        if response.status_code == 400 and "already exists" in response.text:
            # User already exists, try to find and use it
            users_response = await client.get(
                f"{self.base_url}/admin/users?limit=100",
                headers=self.headers
            )
            users = users_response.json()["users"]
            existing = next((u for u in users if u["phone_number"] == phone), None)
            if existing:
                self.test_user_id = existing["id"]
                print(f"(Using existing user ID: {self.test_user_id})", end=" ")
                return

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Missing id field"
        assert data["phone_number"] == phone, f"Phone mismatch: {data['phone_number']} != {phone}"
        self.test_user_id = data["id"]
        print(f"(Created user ID: {self.test_user_id})", end=" ")

    async def test_get_user(self, client: httpx.AsyncClient):
        """Test getting user by ID."""
        assert self.test_user_id is not None, "No test user ID available"
        response = await client.get(
            f"{self.base_url}/admin/users/{self.test_user_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["id"] == self.test_user_id, f"ID mismatch: {data['id']} != {self.test_user_id}"
        print(f"(User ID: {data['id']}, Phone: {data['phone_number']})", end=" ")

    async def test_create_order(self, client: httpx.AsyncClient):
        """Test creating an order."""
        assert self.test_user_id is not None, "No test user ID available"
        response = await client.post(
            f"{self.base_url}/admin/orders",
            headers=self.headers,
            json={
                "user_id": self.test_user_id,
                "status": "pending",
                "total_amount": 300.00,
                "notes": "Test order from admin API"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Missing id field"
        assert data["user_id"] == self.test_user_id, f"User ID mismatch"
        self.test_order_id = data["id"]
        print(f"(Created order ID: {self.test_order_id})", end=" ")

    async def test_get_order(self, client: httpx.AsyncClient):
        """Test getting order by ID with user details."""
        assert self.test_order_id is not None, "No test order ID available"
        response = await client.get(
            f"{self.base_url}/admin/orders/{self.test_order_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["id"] == self.test_order_id, f"ID mismatch"
        assert "user" in data, "Missing user field"
        assert data["user"]["id"] == self.test_user_id, "User ID mismatch in order"
        print(f"(Order ID: {data['id']}, Status: {data['status']})", end=" ")

    async def test_list_orders(self, client: httpx.AsyncClient):
        """Test listing orders."""
        response = await client.get(
            f"{self.base_url}/admin/orders",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "orders" in data, "Missing orders field"
        assert "total" in data, "Missing total field"
        print(f"(Found {data['total']} orders)", end=" ")

    async def test_get_user_orders(self, client: httpx.AsyncClient):
        """Test getting user's orders."""
        assert self.test_user_id is not None, "No test user ID available"
        response = await client.get(
            f"{self.base_url}/admin/users/{self.test_user_id}/orders",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        orders = response.json()
        assert isinstance(orders, list), "Expected list of orders"
        assert len(orders) > 0, "Expected at least one order"
        print(f"(User has {len(orders)} orders)", end=" ")

    async def test_update_order(self, client: httpx.AsyncClient):
        """Test updating an order."""
        assert self.test_order_id is not None, "No test order ID available"
        response = await client.patch(
            f"{self.base_url}/admin/orders/{self.test_order_id}",
            headers=self.headers,
            json={
                "status": "completed",
                "total_amount": 350.00,
                "notes": "Updated via admin API test"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["status"] == "completed", f"Status not updated: {data['status']}"
        assert float(data["total_amount"]) == 350.00, f"Amount not updated: {data['total_amount']}"
        print(f"(Updated to status: {data['status']}, amount: {data['total_amount']})", end=" ")

    async def test_list_orders_filtered(self, client: httpx.AsyncClient):
        """Test listing orders with status filter."""
        response = await client.get(
            f"{self.base_url}/admin/orders?status_filter=completed",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "orders" in data, "Missing orders field"
        # All returned orders should have completed status
        for order in data["orders"]:
            assert order["status"] == "completed", f"Filter failed: got status {order['status']}"
        print(f"(Found {len(data['orders'])} completed orders)", end=" ")

    async def test_delete_order(self, client: httpx.AsyncClient):
        """Test deleting an order."""
        assert self.test_order_id is not None, "No test order ID available"
        response = await client.delete(
            f"{self.base_url}/admin/orders/{self.test_order_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["status"] == "ok", "Deletion not successful"
        print(f"(Deleted order ID: {self.test_order_id})", end=" ")

    async def test_delete_user(self, client: httpx.AsyncClient):
        """Test deleting a user (CASCADE)."""
        assert self.test_user_id is not None, "No test user ID available"
        response = await client.delete(
            f"{self.base_url}/admin/users/{self.test_user_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["status"] == "ok", "Deletion not successful"
        print(f"(Deleted user ID: {self.test_user_id}, orders: {data.get('orders_deleted', 0)})", end=" ")

    async def test_verify_deletion(self, client: httpx.AsyncClient):
        """Verify that deleted entities are gone."""
        # Try to get deleted user
        response = await client.get(
            f"{self.base_url}/admin/users/{self.test_user_id}",
            headers=self.headers
        )
        assert response.status_code == 404, f"User should be deleted, got {response.status_code}"
        print(f"(Verified user deletion)", end=" ")


async def main():
    """Main test runner."""
    # Configuration
    BASE_URL = "http://192.168.1.191:8000"  # Default to Linux server
    ADMIN_KEY = "admin_secret"  # Default admin key

    # Allow command line arguments
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    if len(sys.argv) > 2:
        ADMIN_KEY = sys.argv[2]

    print(f"""
╔══════════════════════════════════════════════════════════╗
║         ADMIN API TEST SUITE                             ║
╚══════════════════════════════════════════════════════════╝

Usage: python test_admin_api.py [BASE_URL] [ADMIN_KEY]

Examples:
  python test_admin_api.py
  python test_admin_api.py http://localhost:8000
  python test_admin_api.py http://192.168.1.191:8000 your_admin_key

""")

    tester = AdminAPITester(BASE_URL, ADMIN_KEY)

    try:
        success = await tester.run_all_tests()
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
