from app.extensions import db
from app.models import (
    AdminUser, Destination, Package, PackageItinerary, Service,
    Vehicle, FixedDeparture, Testimonial, GalleryImage, BlogPost,
    SiteSetting, Guide
)
from datetime import date, timedelta


def seed_if_empty():
    if AdminUser.query.first():
        return

    # Super admin
    admin = AdminUser(
        email='admin@darshannepal.com',
        name='Darshan Admin',
        role='super_admin'
    )
    admin.set_password('Admin@Darshan2024')
    db.session.add(admin)

    # Site settings
    defaults = {
        'business_name': 'Darshan Nepal Travel & Tours',
        'address': 'Urlabari, Koshi Province 56604, Nepal',
        'phone': '9801708396',
        'phones': '9801708396,9801708397,9841110276',
        'email': '',
        'facebook': 'https://www.facebook.com/',
        'instagram': 'https://www.instagram.com/',
        'google_rating': '4.8',
        'review_count': '27',
        'announcement': '',
        'hero_title': 'Discover Nepal. Experience the Extraordinary.',
        'hero_description': 'Explore breathtaking mountains, sacred pilgrimage destinations, hidden valleys and unforgettable journeys with Darshan Nepal Travel & Tours.',
        'hero_eyebrow': 'TRAVEL • EXPLORE • EXPERIENCE NEPAL',
        'default_seo_title': 'Darshan Nepal Travel & Tours | Premium Nepal Tour Packages',
        'default_seo_description': 'Trusted travel agency in Urlabari, Koshi Province. Domestic & international packages, pilgrimage, trekking, vehicle booking & more. 4.8★ Google rating.',
    }
    for k, v in defaults.items():
        db.session.add(SiteSetting(key=k, value=v))

    # Destinations
    destinations_data = [
        {'name': 'Kathmandu', 'slug': 'kathmandu', 'image': 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800&q=80', 'short_description': 'Cultural heart of Nepal with ancient temples and vibrant streets.', 'featured': True},
        {'name': 'Pokhara', 'slug': 'pokhara', 'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&q=80', 'short_description': 'Lakeside paradise beneath the Annapurna range.', 'featured': True},
        {'name': 'Mustang', 'slug': 'mustang', 'image': 'https://images.unsplash.com/photo-1571401835393-8c5f35328320?w=800&q=80', 'short_description': 'The forbidden kingdom of high desert landscapes and ancient caves.', 'featured': True},
        {'name': 'Rara Lake', 'slug': 'rara-lake', 'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80', 'short_description': 'Nepal\'s largest and most pristine alpine lake.', 'featured': True},
        {'name': 'Pathibhara', 'slug': 'pathibhara', 'image': 'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?w=800&q=80', 'short_description': 'Sacred temple of Goddess Pathibhara in eastern Nepal.', 'featured': True},
        {'name': 'Kalinchowk', 'slug': 'kalinchowk', 'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80', 'short_description': 'Hilltop temple with panoramic Himalayan views.', 'featured': True},
        {'name': 'Shree Antu / Ilam', 'slug': 'shree-antu', 'image': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80', 'short_description': 'Tea gardens and sunrise views over the eastern hills.', 'featured': True},
        {'name': 'Chitwan', 'slug': 'chitwan', 'image': 'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=800&q=80', 'short_description': 'Wildlife sanctuary of rhinos, tigers and jungle adventures.', 'featured': True},
        {'name': 'Darjeeling', 'slug': 'darjeeling', 'image': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800&q=80', 'short_description': 'Queen of the Hills — tea estates and Himalayan vistas.', 'featured': False},
        {'name': 'Sikkim', 'slug': 'sikkim', 'image': 'https://images.unsplash.com/photo-1582510003544-4d00b8f52249?w=800&q=80', 'short_description': 'Mountain state of monasteries and alpine beauty.', 'featured': False},
    ]
    dest_map = {}
    for i, d in enumerate(destinations_data):
        dest = Destination(
            name=d['name'],
            slug=d['slug'],
            short_description=d['short_description'],
            description=d['short_description'] + ' Experience authentic Nepal with Darshan Nepal Travel & Tours.',
            best_time='September to May',
            featured_image=d.get('image'),
            status='published',
            featured=d['featured'],
            sort_order=i,
            seo_title=f"{d['name']} Tour Packages | Darshan Nepal Travel",
            seo_description=d['short_description'],
        )
        db.session.add(dest)
        dest_map[d['slug']] = dest

    db.session.flush()

    # Packages
    packages_data = [
        {
            'title': '15 Days Badri-Kedar Tour Package',
            'slug': '15-days-badri-kedar-tour',
            'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&q=80',
            'short_description': 'Sacred pilgrimage to Badrinath and Kedarnath — a spiritual journey through the Himalayas.',
            'destination': 'Badri-Kedar',
            'duration': '15 Days',
            'duration_days': 15,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Pilgrimage',
            'difficulty': 'Moderate',
            'featured': True,
            'highlights': 'Badrinath Temple\nKedarnath Temple\nHaridwar\nRishikesh\nSpiritual darshan',
        },
        {
            'title': '2 Days Shree Antu Tour Package',
            'slug': '2-days-shree-antu-tour',
            'image': 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800&q=80',
            'short_description': 'Short escape to the tea hills of Ilam with sunrise views from Shree Antu.',
            'destination': 'Shree Antu',
            'duration': '2 Days',
            'duration_days': 2,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Sightseeing',
            'difficulty': 'Easy',
            'featured': True,
            'highlights': 'Shree Antu viewpoint\nTea gardens of Ilam\nSunrise experience\nLocal culture',
        },
        {
            'title': '22 Days Gaya Kashi Char Dham Tour Package',
            'slug': '22-days-gaya-kashi-char-dham-tour',
            'image': 'https://images.unsplash.com/photo-1582510003544-4d00b8f52249?w=800&q=80',
            'short_description': 'Complete Char Dham yatra covering Gaya, Kashi and the four sacred abodes.',
            'destination': 'Char Dham',
            'duration': '22 Days',
            'duration_days': 22,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Pilgrimage',
            'difficulty': 'Moderate',
            'featured': True,
            'highlights': 'Char Dham temples\nGaya\nKashi (Varanasi)\nFull spiritual circuit',
        },
        {
            'title': '3 Days Kalinchowk Tour Package',
            'slug': '3-days-kalinchowk-tour',
            'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
            'short_description': 'Weekend pilgrimage and mountain views at Kalinchowk Bhagwati Temple.',
            'destination': 'Kalinchowk',
            'duration': '3 Days',
            'duration_days': 3,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Pilgrimage',
            'difficulty': 'Easy',
            'featured': True,
            'highlights': 'Kalinchowk Temple\nHimalayan panorama\nCable car option\nLocal hospitality',
        },
        {
            'title': '3 Days Pathibhara Tour Package',
            'slug': '3-days-pathibhara-tour',
            'image': 'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?w=800&q=80',
            'short_description': 'Visit the powerful Pathibhara Devi temple in the hills of Taplejung.',
            'destination': 'Pathibhara',
            'duration': '3 Days',
            'duration_days': 3,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Pilgrimage',
            'difficulty': 'Moderate',
            'featured': True,
            'highlights': 'Pathibhara Temple\nEastern Nepal hills\nDevotional atmosphere\nScenic drives',
        },
        {
            'title': '4 Days Darjeeling Sikkim Tour Package',
            'slug': '4-days-darjeeling-sikkim-tour',
            'image': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800&q=80',
            'short_description': 'Cross-border journey through tea gardens, monasteries and mountain towns.',
            'destination': 'Darjeeling & Sikkim',
            'duration': '4 Days',
            'duration_days': 4,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Sightseeing',
            'difficulty': 'Easy',
            'featured': True,
            'highlights': 'Darjeeling tea estates\nTiger Hill sunrise\nSikkim monasteries\nMountain roads',
        },
        {
            'title': '6 Days Mustang Tour Package',
            'slug': '6-days-mustang-tour',
            'image': 'https://images.unsplash.com/photo-1571401835393-8c5f35328320?w=800&q=80',
            'short_description': 'Explore the rain-shadow kingdom of Upper and Lower Mustang.',
            'destination': 'Mustang',
            'duration': '6 Days',
            'duration_days': 6,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Adventure',
            'difficulty': 'Moderate',
            'featured': True,
            'highlights': 'Lo Manthang\nAncient caves\nDesert landscapes\nTibetan culture',
        },
        {
            'title': '9 Days Rara Lake Tour Package',
            'slug': '9-days-rara-lake-tour',
            'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80',
            'short_description': 'Journey to Nepal\'s largest alpine lake in the remote west.',
            'destination': 'Rara Lake',
            'duration': '9 Days',
            'duration_days': 9,
            'starting_price': 'On Request',
            'price_type': 'On Request',
            'travel_type': 'Adventure',
            'difficulty': 'Moderate',
            'featured': True,
            'highlights': 'Rara Lake\nRara National Park\nRemote western Nepal\nAlpine wilderness',
        },
    ]

    for i, p in enumerate(packages_data):
        pkg = Package(
            title=p['title'],
            slug=p['slug'],
            short_description=p['short_description'],
            full_description=p['short_description'] + '\n\nJoin Darshan Nepal Travel & Tours for a carefully planned itinerary with experienced local support. Contact us for custom dates, group sizes and pricing.',
            destination=p['destination'],
            duration=p['duration'],
            duration_days=p['duration_days'],
            starting_price=p['starting_price'],
            price_type=p['price_type'],
            travel_type=p['travel_type'],
            difficulty=p['difficulty'],
            featured_image=p.get('image'),
            highlights=p['highlights'],
            included='Transportation as per itinerary\nAccommodation\nLocal guide support\nBasic meals as specified',
            excluded='Personal expenses\nTravel insurance\nTips\nExtra activities not listed',
            best_time='September to May (varies by destination)',
            status='published',
            featured=p['featured'],
            sort_order=i,
            seo_title=f"{p['title']} | Darshan Nepal Travel & Tours",
            seo_description=p['short_description'],
        )
        db.session.add(pkg)

    db.session.flush()

    # Services
    services = [
        ('Air Ticketing', 'air-ticketing', 'Domestic and international flight bookings.'),
        ('Vehicle Booking', 'vehicle-booking', 'Cars, jeeps, vans and buses for your journey.'),
        ('Vehicle Hire', 'vehicle-hire', 'Self-drive and chauffeur-driven vehicle hire.'),
        ('Helicopter Services', 'helicopter-services', 'Helicopter transfers and scenic flights (on request).'),
        ('Guiding Service', 'guiding-service', 'Experienced local guides for treks and tours.'),
        ('Trekking & Hiking', 'trekking-hiking', 'Guided treks and day hikes across Nepal.'),
        ('Pilgrimage Tours', 'pilgrimage-tours', 'Sacred journeys to temples and holy sites.'),
        ('School Travel', 'school-travel', 'Educational and fun trips for schools.'),
        ('Team Travel', 'team-travel', 'Corporate and group team-building trips.'),
        ('Sightseeing', 'sightseeing', 'City and regional sightseeing tours.'),
        ('Fixed Departure', 'fixed-departure', 'Scheduled group departures with set dates.'),
        ('Online Travel Service', 'online-travel-service', 'Plan and enquire online from anywhere.'),
    ]
    for i, (title, slug, desc) in enumerate(services):
        db.session.add(Service(title=title, slug=slug, description=desc, status='published', sort_order=i))

    # Vehicles
    vehicles = [
        ('Toyota Hiace', 'Hiace', 'Hiace', 12, True, True),
        ('Scorpio Jeep', 'Jeep', 'Scorpio', 7, True, False),
        ('Toyota Innova', 'Car', 'Innova', 6, True, True),
        ('Tourist Bus', 'Tourist Bus', 'Deluxe', 30, True, True),
        ('Micro Bus', 'Van', 'Micro', 15, True, True),
    ]
    for name, vtype, model, cap, driver, ac in vehicles:
        db.session.add(Vehicle(
            name=name, vehicle_type=vtype, model=model, capacity=cap,
            driver_included=driver, ac=ac, price='On Request', price_type='Per Day',
            availability='available', status='published',
            description=f'{name} available for hire with driver. Contact for rates.'
        ))

    # Guides
    db.session.add(Guide(
        name='Local Guide Team',
        position='Travel Guides',
        bio='Our experienced local guides know the routes, culture and safety practices across Nepal.',
        languages='Nepali, Hindi, English',
        specialization='Trekking, Pilgrimage, Cultural tours',
        experience='Experienced team',
        status='active'
    ))

    # Testimonials (placeholders clearly marked)
    db.session.add(Testimonial(
        name='Traveler',
        location='Nepal',
        review='Placeholder review — actual Google reviews available on our Google Business profile. Rating 4.8/5 from 27 reviews.',
        rating=5,
        verified=False,
        featured=True,
        status='published'
    ))


    # Gallery sample images
    gallery_samples = [
        ('https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&q=80', 'Mountains', 'Himalayan peaks'),
        ('https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80', 'Lakes', 'Alpine lake'),
        ('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80', 'Mountains', 'Mountain ridge'),
        ('https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800&q=80', 'Culture', 'Nepal culture'),
        ('https://images.unsplash.com/photo-1518002171953-a080ee817e1f?w=800&q=80', 'Temples', 'Temple architecture'),
        ('https://images.unsplash.com/photo-1571401835393-8c5f35328320?w=800&q=80', 'Trekking', 'Mustang landscape'),
    ]
    for i, (url, cat, alt) in enumerate(gallery_samples):
        db.session.add(GalleryImage(image_url=url, category=cat, alt_text=alt, caption=alt, status='published', sort_order=i))

    # Blog sample
    db.session.add(BlogPost(
        title='Planning Your First Trip to Mustang',
        slug='planning-first-trip-mustang',
        excerpt='Essential tips for visiting the former forbidden kingdom of Mustang.',
        content='Mustang offers unique high-desert landscapes and Tibetan-influenced culture. Best visited in spring or autumn. Permits are required for Upper Mustang. Contact Darshan Nepal Travel for itinerary and logistics support.',
        author='Darshan Nepal Travel',
        category='Destination Guide',
        tags='Mustang, Adventure, Nepal',
        status='published',
        seo_title='Planning Your First Trip to Mustang | Darshan Nepal Travel',
        seo_description='Tips for visiting Mustang with Darshan Nepal Travel & Tours.',
    ))

    db.session.commit()
    print('Database seeded successfully.')
