from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Concert, ConcertAttending

class BandSiteTests(TestCase):
    def setUp(self):
        self.concert = Concert.objects.create(concert_name='Coachella 2023', duration=72, city='Indio, California', date='2023-04-14')
        self.user = User.objects.create_user('testfan', password='local-test-password')

    def test_home_concerts_and_login(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertContains(self.client.get('/concerts/'), 'Coachella 2023')
        self.assertRedirects(self.client.get(f'/concert-detail/{self.concert.id}'), f'/login/?next=/concert-detail/{self.concert.id}')
        self.assertEqual(self.client.post('/login/', {'username':'testfan','password':'wrong'}).status_code, 200)
        self.assertRedirects(self.client.post('/login/', {'username':'testfan','password':'local-test-password'}), '/')

    def test_rsvp_updates_single_record(self):
        self.client.force_login(self.user)
        payload = {'concert_id': self.concert.id, 'attendee_choice': 'Attending'}
        self.assertRedirects(self.client.post('/concert_attendee/', payload), '/concerts/')
        payload['attendee_choice'] = 'Not Attending'
        self.client.post('/concert_attendee/', payload)
        self.assertEqual(ConcertAttending.objects.count(), 1)
        self.assertEqual(ConcertAttending.objects.get().attending, 'Not Attending')
        payload['attendee_choice'] = 'invalid'
        self.assertEqual(self.client.post('/concert_attendee/', payload).status_code, 400)

    @patch('concert.views.requests.get')
    def test_services_render_and_lyrics_modal(self, get):
        get.return_value = Mock(json=lambda: [{'id':1,'title':'Test Song','lyrics':'Test lyrics'}])
        response = self.client.get('/songs/')
        self.assertContains(response, 'Test Song')
        self.assertContains(response, 'Test lyrics')
        self.assertContains(response, 'data-bs-toggle="modal"')
        photo = {'id':1,'pic_url':'https://example.com/photo.jpg','event_city':'Indio','event_state':'California','event_country':'US','event_date':'2023-04-14'}
        get.return_value = Mock(json=lambda: [photo])
        self.assertContains(self.client.get('/photos/'), '/photos/1/')
        get.return_value = Mock(json=lambda: photo)
        self.assertContains(self.client.get('/photos/1/'), 'Indio')

    @patch('concert.views.requests.get')
    def test_service_failure_is_explicit(self, get):
        import requests
        get.side_effect = requests.ConnectionError()
        self.assertEqual(self.client.get('/songs/').status_code, 503)
        self.assertEqual(self.client.get('/photos/').status_code, 503)
