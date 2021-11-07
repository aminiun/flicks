from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.account.models import PhoneOTP

User = get_user_model()


class TestAuth(APITestCase):

    def tearDown(self) -> None:
        cache.clear()

    def test_send_otp_for_not_existed_phone_success(self):
        response = self.client.post(
            reverse('auth-send_otp'),
            data={
                "phone": "+989122222111",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json().get('id', None))
        self.assertEqual(response.json()['phone'], "+989122222111")

        user = PhoneOTP.active_objects.get(phone="+989122222111")
        self.assertTrue(user.has_otp)

    def test_send_otp_for_existed_phone_before_time_limit_raise_validation_error_400(self):
        unverified_user = PhoneOTP.objects.create(
            phone='+989122222111',
        )
        unverified_user.set_otp()
        response = self.client.post(
            reverse('auth-send_otp'),
            data={
                "phone": "+989122222111",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['details'], "Try getting otp after 1 min")

    def test_send_otp_for_existed_phone_in_phoneotp_model_success(self):
        unverified_user = PhoneOTP.objects.create(
            phone='+989122222111',
        )
        response = self.client.post(
            reverse('auth-send_otp'),
            data={
                "phone": "+989122222111",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json().get('id', None))
        self.assertEqual(response.json()['phone'], "+989122222111")

        user = PhoneOTP.active_objects.get(phone="+989122222111")
        self.assertTrue(user.has_otp)

    def test_send_otp_for_existed_phone_in_user_model_raise_validation_error_400(self):
        verified_user = User.objects.create(
            username='test',
            phone='+989122222111'
        )
        response = self.client.post(
            reverse('auth-send_otp'),
            data={
                "phone": "+989122222111",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['details'], ["User with that phone number already existed"])

    def test_send_otp_for_wrong_phone_number_raise_validation_error_400(self):
        response = self.client.post(
            reverse('auth-send_otp'),
            data={
                "phone": "09122222111",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_verify_otp_for_existed_phoneotp_model_and_existed_otp_with_right_otp_success(self):
        unverified_user = PhoneOTP.objects.create(
            phone='+989122222111',
        )
        otp = unverified_user.set_otp()
        response = self.client.post(
            reverse('auth-verify', kwargs={'pk': unverified_user.id}),
            data={
                "otp": "1234",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('id', None))

        self.assertTrue(unverified_user.is_verified)

    def test_verify_otp_for_not_existed_phoneotp_model_raise_404_not_found(self):
        response = self.client.post(
            reverse('auth-verify', kwargs={'pk': 1}),
            data={
                "otp": "1234",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_verify_otp_for_existed_phoneotp_model_and_existed_otp_with_wrong_otp_raise_400(self):
        unverified_user = PhoneOTP.objects.create(
            phone='+989122222111',
        )
        otp = unverified_user.set_otp()
        response = self.client.post(
            reverse('auth-verify', kwargs={'pk': unverified_user.id}),
            data={
                "otp": "123456",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['details'], 'OTP wrong!')

    def test_verify_otp_for_existed_phoneotp_model_and_not_existed_otp_raise_400(self):
        unverified_user = PhoneOTP.objects.create(
            phone='+989122222111',
        )
        response = self.client.post(
            reverse('auth-verify', kwargs={'pk': unverified_user.id}),
            data={
                "otp": "123456",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['details'], 'OTP wrong!')

    def test_register_new_user_with_verified_phone_success(self):
        verified_user = PhoneOTP.objects.create(
            phone='+989122222111',
        )
        verified_user.verify()
        response = self.client.post(
            reverse('auth-register'),
            data={
                "phone": "+989122222111",
                "username": "test",
                "password": "test",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.active_objects.active().filter(username="test", phone="+989122222111").exists()
        )

    def test_register_new_user_with_unverified_phone_raise_validation_error_400(self):
        verified_user = PhoneOTP.objects.create(
            phone='+989122222111',
        )
        response = self.client.post(
            reverse('auth-register'),
            data={
                "phone": "+989122222111",
                "username": "test",
                "password": "test",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['details'], ['first verify phone number'])

    def test_register_existed_user_raise_400(self):
        existed_user = User.objects.create(
            phone='+989122222111',
            username='test',
        )
        response = self.client.post(
            reverse('auth-register'),
            data={
                "phone": "+989122222111",
                "username": "test",
                "password": "test",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_new_user_with_existed_username_raise_validation_error_400(self):
        existed_user = User.objects.create(
            phone='+989122222111',
            username='test1',
        )
        response = self.client.post(
            reverse('auth-register'),
            data={
                "phone": "+989122222111",
                "username": "test",
                "password": "test",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_new_user_with_existed_phone_raise_validation_error_400(self):
        existed_user = User.objects.create(
            phone='+989122222112',
            username='test',
        )
        response = self.client.post(
            reverse('auth-register'),
            data={
                "phone": "+989122222111",
                "username": "test",
                "password": "test",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_login_with_not_existed_user_raise_404_error(self):
        response = self.client.post(
            reverse('auth-login'),
            data={
                "phone_username": "+989191234567",
                "password": "string"
            },
            format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_login_with_existed_user_with_invalid_password_raise_401_error(self):
        user = User.objects.create_user(username='test', phone='+989191234567', password='pass')
        response = self.client.post(
            reverse('auth-login'),
            data={
                "phone_username": "+989191234567",
                "password": "string1"
            },
            format='json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['details'], 'Username or password is wrong!')

    def test_login_with_existed_user_with_phone_success(self):
        user = User.objects.create_user(username='test', phone='+989191234567', password='pass')
        response = self.client.post(
            reverse('auth-login'),
            data={
                "phone_username": "+989191234567",
                "password": "pass"
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_login_with_existed_user_with_username_success(self):
        user = User.objects.create_user(
            username='test',
            phone='+989191234567',
            password='pass'
        )
        response = self.client.post(
            reverse('auth-login'),
            data={
                "phone_username": "test",
                "password": "pass"
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_check_username_with_existed_username_success(self):
        user = User.objects.create_user(
            username='test',
            phone='+989191234567',
            password='pass'
        )
        response = self.client.post(
            reverse('auth-check_username'),
            data={
                "username": "test",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['details'], True)

    def test_check_username_with_not_existed_username_success(self):
        response = self.client.post(
            reverse('auth-check_username'),
            data={
                "username": "test",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['details'], False)

    def test_forget_password_otp_with_not_existed_user_raise_404(self):
        response = self.client.post(
            reverse('auth-forget_password_otp'),
            data={
                "phone": "+989191234567",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_forget_password_otp_with_existed_user_success(self):
        otp = PhoneOTP.objects.create(phone='+989191234567')
        User.objects.create_user(
            username='test',
            phone='+989191234567',
            password='pass'
        )
        response = self.client.post(
            reverse('auth-forget_password_otp'),
            data={
                "phone": "+989191234567",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json()['id'])
        self.assertTrue(otp.has_otp)

    def test_forget_password_change_with_not_existed_phoneotp_raise_404(self):
        response = self.client.post(
            reverse('auth-forget_password_change', kwargs={'pk': 1}),
            data={
                "phone": "+989191234567",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_forget_password_change_with_not_verified_phone_raise_400(self):
        otp = PhoneOTP.objects.create(phone='+989191234567')
        response = self.client.post(
            reverse('auth-forget_password_change', kwargs={'pk': 1}),
            data={
                "phone": "+989191234567",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['details'], 'first verify phone number')

    def test_forget_password_change_with_verified_phone_success(self):
        otp = PhoneOTP.objects.create(phone='+989191234567')
        User.objects.create_user(
            username='test',
            phone='+989191234567',
            password='pass'
        )
        otp.verify()
        response = self.client.post(
            reverse('auth-forget_password_change', kwargs={'pk': otp.id}),
            data={
                "password": "new",
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['details'], "Password changed successfully")
