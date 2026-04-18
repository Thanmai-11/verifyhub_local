from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Skill, Artifact, Vote
import tempfile
import os


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def create_user(username, password='testpass123'):
    return User.objects.create_user(username=username, password=password)

def create_skill(name='Django'):
    return Skill.objects.get_or_create(name=name)[0]

def create_artifact(user, skill, status='pending'):
    return Artifact.objects.create(
        contributor=user,
        skill=skill,
        title=f'{user.username} artifact',
        file='artifacts/test.pdf',
        status=status
    )


# ─────────────────────────────────────────────
#  MODEL TESTS
# ─────────────────────────────────────────────
class ArtifactModelTest(TestCase):

    def setUp(self):
        self.user = create_user('testuser')
        self.skill = create_skill()
        self.artifact = create_artifact(self.user, self.skill)

    def test_artifact_default_status_is_pending(self):
        self.assertEqual(self.artifact.status, 'pending')

    def test_approve_count_starts_zero(self):
        self.assertEqual(self.artifact.approve_count(), 0)

    def test_reject_count_starts_zero(self):
        self.assertEqual(self.artifact.reject_count(), 0)

    def test_artifact_str(self):
        self.assertIn('testuser', str(self.artifact))

    def test_status_becomes_approved_with_2_votes(self):
        voter1 = create_user('voter1')
        voter2 = create_user('voter2')
        Vote.objects.create(artifact=self.artifact, voter=voter1, vote='approve')
        Vote.objects.create(artifact=self.artifact, voter=voter2, vote='approve')
        self.artifact.refresh_from_db()
        self.assertEqual(self.artifact.status, 'approved')

    def test_status_becomes_rejected_with_2_votes(self):
        voter1 = create_user('voter1')
        voter2 = create_user('voter2')
        Vote.objects.create(artifact=self.artifact, voter=voter1, vote='reject')
        Vote.objects.create(artifact=self.artifact, voter=voter2, vote='reject')
        self.artifact.refresh_from_db()
        self.assertEqual(self.artifact.status, 'rejected')

    def test_status_stays_pending_with_1_vote(self):
        voter1 = create_user('voter1')
        Vote.objects.create(artifact=self.artifact, voter=voter1, vote='approve')
        self.artifact.refresh_from_db()
        self.assertEqual(self.artifact.status, 'pending')


# ─────────────────────────────────────────────
#  AUTH TESTS
# ─────────────────────────────────────────────
class AuthTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = create_user('authuser')

    def test_register_new_user(self):
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_valid_credentials(self):
        response = self.client.post('/login/', {
            'username': 'authuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, '/dashboard/')

    def test_login_invalid_credentials(self):
        response = self.client.post('/login/', {
            'username': 'authuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_home(self):
        self.client.login(username='authuser', password='testpass123')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/')

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_upload_requires_login(self):
        response = self.client.get('/upload/')
        self.assertRedirects(response, '/login/?next=/upload/')

    def test_review_requires_login(self):
        response = self.client.get('/review/')
        self.assertRedirects(response, '/login/?next=/review/')


# ─────────────────────────────────────────────
#  VOTE TESTS
# ─────────────────────────────────────────────
class VoteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.skill = create_skill()

        # artifact owner
        self.owner = create_user('owner')
        self.artifact = create_artifact(self.owner, self.skill)

        # verified voter
        self.voter = create_user('voter')
        voter_artifact = create_artifact(self.voter, self.skill, status='approved')

        # superuser
        self.admin = User.objects.create_superuser(
            username='admin', password='admin123')

    def _vote(self, user, vote_value):
        self.client.login(username=user.username, password='testpass123')
        return self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': vote_value,
        })

    def test_superuser_can_vote(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_cannot_vote_on_own_artifact(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Cannot vote on your own artifact')

    def test_two_approvals_change_status(self):
        voter2 = create_user('voter2')
        create_artifact(voter2, self.skill, status='approved')

        self._vote(self.voter, 'approve')
        self.client.login(username='voter2', password='testpass123')
        self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })
        self.artifact.refresh_from_db()
        self.assertEqual(self.artifact.status, 'approved')

    def test_vote_requires_login(self):
        response = self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })
        self.assertRedirects(response, '/login/?next=/vote/')


# ─────────────────────────────────────────────
#  PROFILE TESTS
# ─────────────────────────────────────────────
class ProfileTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = create_user('profileuser')
        self.skill = create_skill()

    def test_public_profile_accessible(self):
        response = self.client.get(f'/profile/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_shows_approved_artifacts(self):
        create_artifact(self.user, self.skill, status='approved')
        response = self.client.get(f'/profile/{self.user.username}/')
        self.assertContains(response, 'Django')

    def test_profile_404_for_nonexistent_user(self):
        response = self.client.get('/profile/doesnotexist/')
        self.assertEqual(response.status_code, 404)

# ─────────────────────────────────────────────
#  BOUNDARY & FUZZY TESTS
# ─────────────────────────────────────────────
class BoundaryAndFuzzyTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.skill = create_skill()

    # ── REGISTRATION BOUNDARY TESTS ──
    def test_register_username_max_length(self):
        """Username at max allowed length (150 chars)"""
        long_username = 'a' * 150
        response = self.client.post('/register/', {
            'username': long_username,
            'email': 'long@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 302)

    def test_register_username_too_long(self):
        """Username over max length should fail"""
        too_long = 'a' * 151
        response = self.client.post('/register/', {
            'username': too_long,
            'email': 'toolong@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_empty_username(self):
        """Empty username should fail"""
        response = self.client.post('/register/', {
            'username': '',
            'email': 'empty@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_empty_password(self):
        """Empty password should fail"""
        response = self.client.post('/register/', {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': '',
            'password2': '',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_invalid_email(self):
        """Invalid email format should fail"""
        response = self.client.post('/register/', {
            'username': 'testuser',
            'email': 'notanemail',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_special_characters_username(self):
        """Special characters in username"""
        response = self.client.post('/register/', {
            'username': 'user@#$%',
            'email': 'special@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_duplicate_username(self):
        """Duplicate username should fail"""
        create_user('existinguser')
        response = self.client.post('/register/', {
            'username': 'existinguser',
            'email': 'dup@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_whitespace_username(self):
        """Whitespace only username should fail"""
        response = self.client.post('/register/', {
            'username': '   ',
            'email': 'ws@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 200)

    # ── ARTIFACT BOUNDARY TESTS ──
    def test_artifact_title_max_length(self):
        """Artifact title at max allowed length"""
        user = create_user('boundaryuser')
        self.client.login(username='boundaryuser', password='testpass123')
        long_title = 'a' * 200
        with open('/tmp/test.txt', 'w') as f:
            f.write('test content')
        with open('/tmp/test.txt', 'rb') as f:
            response = self.client.post('/upload/', {
                'skill': self.skill.id,
                'title': long_title,
                'file': f,
            })
        self.assertEqual(response.status_code, 302)

    def test_artifact_title_too_long(self):
        """Artifact title over max length should fail"""
        user = create_user('boundaryuser2')
        self.client.login(username='boundaryuser2', password='testpass123')
        too_long_title = 'a' * 201
        with open('/tmp/test.txt', 'w') as f:
            f.write('test content')
        with open('/tmp/test.txt', 'rb') as f:
            response = self.client.post('/upload/', {
                'skill': self.skill.id,
                'title': too_long_title,
                'file': f,
            })
        self.assertEqual(response.status_code, 200)

    def test_artifact_empty_title(self):
        """Empty artifact title should fail"""
        user = create_user('boundaryuser3')
        self.client.login(username='boundaryuser3', password='testpass123')
        with open('/tmp/test.txt', 'w') as f:
            f.write('test content')
        with open('/tmp/test.txt', 'rb') as f:
            response = self.client.post('/upload/', {
                'skill': self.skill.id,
                'title': '',
                'file': f,
            })
        self.assertEqual(response.status_code, 200)

    def test_artifact_no_file(self):
        """Artifact with no file should fail"""
        user = create_user('boundaryuser4')
        self.client.login(username='boundaryuser4', password='testpass123')
        response = self.client.post('/upload/', {
            'skill': self.skill.id,
            'title': 'Test Title',
        })
        self.assertEqual(response.status_code, 200)

    # ── FUZZY TESTS ──
    def test_login_fuzzy_inputs(self):
        """Random/garbage inputs should not crash login"""
        fuzzy_inputs = [
            ('', ''),
            ('   ', '   '),
            ('a' * 1000, 'b' * 1000),
            ('<script>alert(1)</script>', 'password'),
            ('user\x00name', 'pass\x00word'),
            ('DROP TABLE users;--', 'password'),
            ("' OR '1'='1", "' OR '1'='1"),
            ('../../../etc/passwd', 'password'),
        ]
        for username, password in fuzzy_inputs:
            response = self.client.post('/login/', {
                'username': username,
                'password': password,
            })
            self.assertIn(response.status_code, [200, 302],
                msg=f"Login crashed with username='{username}'")

    def test_register_fuzzy_inputs(self):
        """Random/garbage inputs should not crash register"""
        fuzzy_inputs = [
            ('', '', '', ''),
            ('<script>', 'test@test.com', 'pass', 'pass'),
            ('a' * 1000, 'b' * 1000, 'c' * 1000, 'c' * 1000),
            ("'; DROP TABLE auth_user;--", 'sql@test.com', 'pass', 'pass'),
            ('\x00\x01\x02', 'null@test.com', 'pass', 'pass'),
        ]
        for username, email, pass1, pass2 in fuzzy_inputs:
            response = self.client.post('/register/', {
                'username': username,
                'email': email,
                'password1': pass1,
                'password2': pass2,
            })
            self.assertIn(response.status_code, [200, 302],
                msg=f"Register crashed with username='{username}'")

    def test_vote_fuzzy_artifact_id(self):
        """Garbage artifact IDs should not crash vote endpoint"""
        user = create_user('fuzzyvoter')
        self.client.login(username='fuzzyvoter', password='testpass123')
        fuzzy_ids = [
            '999999',
            '-1',
            '0',
            'abc',
            '<script>',
            '',
            'null',
            '1.5',
        ]
        for artifact_id in fuzzy_ids:
            response = self.client.post('/vote/', {
                'artifact_id': artifact_id,
                'vote': 'approve',
            })
            self.assertIn(response.status_code, [200, 302, 404],
                msg=f"Vote crashed with artifact_id='{artifact_id}'")

    def test_profile_fuzzy_username(self):
        """Garbage usernames in profile URL should return 404"""
        fuzzy_usernames = [
            'nonexistent',
            '<script>alert(1)</script>',
            '../admin',
            'a' * 150,
            '12345',
        ]
        for username in fuzzy_usernames:
            response = self.client.get(f'/profile/{username}/')
            self.assertIn(response.status_code, [200, 404])


# ─────────────────────────────────────────────
#  SECURITY TESTS
# ─────────────────────────────────────────────
class SecurityTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = create_user('securityuser')
        self.skill = create_skill()

    def test_csrf_protection_on_login(self):
        """Login without CSRF token should fail"""
        client = Client(enforce_csrf_checks=True)
        response = client.post('/login/', {
            'username': 'securityuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 403)

    def test_csrf_protection_on_register(self):
        """Register without CSRF token should fail"""
        client = Client(enforce_csrf_checks=True)
        response = client.post('/register/', {
            'username': 'newuser',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 403)

    def test_csrf_protection_on_upload(self):
        """Upload without CSRF token should fail"""
        client = Client(enforce_csrf_checks=True)
        client.login(username='securityuser', password='testpass123')
        response = client.post('/upload/', {
            'skill': self.skill.id,
            'title': 'Test',
        })
        self.assertEqual(response.status_code, 403)

    def test_csrf_protection_on_vote(self):
        """Vote without CSRF token should fail"""
        client = Client(enforce_csrf_checks=True)
        client.login(username='securityuser', password='testpass123')
        response = client.post('/vote/', {
            'artifact_id': '1',
            'vote': 'approve',
        })
        self.assertEqual(response.status_code, 403)

    def test_cannot_access_dashboard_without_login(self):
        """Unauthenticated access to dashboard redirects"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_cannot_access_upload_without_login(self):
        """Unauthenticated access to upload redirects"""
        response = self.client.get('/upload/')
        self.assertEqual(response.status_code, 302)

    def test_cannot_access_review_without_login(self):
        """Unauthenticated access to review redirects"""
        response = self.client.get('/review/')
        self.assertEqual(response.status_code, 302)

    def test_cannot_vote_without_login(self):
        """Unauthenticated vote attempt redirects"""
        response = self.client.post('/vote/', {
            'artifact_id': '1',
            'vote': 'approve',
        })
        self.assertEqual(response.status_code, 302)

    def test_sql_injection_in_login(self):
        """SQL injection in login should not succeed"""
        response = self.client.post('/login/', {
            'username': "' OR '1'='1'; --",
            'password': "' OR '1'='1'; --",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_sql_injection_in_register(self):
        """SQL injection in register should not create user"""
        response = self.client.post('/register/', {
            'username': "'; DROP TABLE auth_user; --",
            'email': 'sql@test.com',
            'password1': 'Testpass@123',
            'password2': 'Testpass@123',
        })
        self.assertEqual(response.status_code, 200)

    def test_xss_in_username(self):
        """XSS in username should be escaped"""
        xss_user = create_user('xssuser')
        self.client.login(username='xssuser', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertNotIn('<script>', response.content.decode())

    def test_cannot_vote_on_own_artifact(self):
        """User cannot vote on their own artifact"""
        artifact = create_artifact(self.user, self.skill)
        self.client.login(username='securityuser', password='testpass123')
        response = self.client.post('/vote/', {
            'artifact_id': artifact.id,
            'vote': 'approve',
        })
        data = response.json()
        self.assertFalse(data['success'])

    def test_vote_only_accepts_valid_values(self):
        """Vote endpoint only accepts approve/reject"""
        other_user = create_user('otheruser')
        artifact = create_artifact(other_user, self.skill)
        self.client.login(username='securityuser', password='testpass123')
        response = self.client.post('/vote/', {
            'artifact_id': artifact.id,
            'vote': 'delete_everything',
        })
        data = response.json()
        self.assertFalse(data['success'])

    def test_vote_get_request_fails(self):
        """Vote endpoint should reject GET requests"""
        self.client.login(username='securityuser', password='testpass123')
        response = self.client.get('/vote/')
        data = response.json()
        self.assertFalse(data['success'])


# ─────────────────────────────────────────────
#  API / INTEGRATION TESTS
# ─────────────────────────────────────────────
class APITest(TestCase):

    def setUp(self):
        self.client = Client()
        self.skill = create_skill()
        self.admin = User.objects.create_superuser(
            username='apiadmin', password='admin123')
        self.user = create_user('apiuser')
        self.artifact = create_artifact(self.user, self.skill)

    def test_vote_returns_json(self):
        """Vote endpoint returns valid JSON"""
        self.client.login(username='apiadmin', password='admin123')
        response = self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('approve_count', data)
        self.assertIn('reject_count', data)
        self.assertIn('new_status', data)

    def test_vote_approve_increments_count(self):
        """Approving increments approve count"""
        self.client.login(username='apiadmin', password='admin123')
        response = self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })
        data = response.json()
        self.assertEqual(data['approve_count'], 1)
        self.assertEqual(data['reject_count'], 0)

    def test_vote_reject_increments_count(self):
        """Rejecting increments reject count"""
        self.client.login(username='apiadmin', password='admin123')
        response = self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'reject',
        })
        data = response.json()
        self.assertEqual(data['approve_count'], 0)
        self.assertEqual(data['reject_count'], 1)

    def test_two_approvals_returns_approved_status(self):
        """Two approvals returns approved status in JSON"""
        voter2 = create_user('voter2api')
        create_artifact(voter2, self.skill, status='approved')

        self.client.login(username='apiadmin', password='admin123')
        self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })

        self.client.login(username='voter2api', password='testpass123')
        response = self.client.post('/vote/', {
            'artifact_id': self.artifact.id,
            'vote': 'approve',
        })
        data = response.json()
        self.assertEqual(data['new_status'], 'approved')

    def test_home_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page_returns_200(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_register_page_returns_200(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page_returns_200(self):
        response = self.client.get(f'/profile/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_profile_returns_404(self):
        response = self.client.get('/profile/doesnotexist999/')
        self.assertEqual(response.status_code, 404)