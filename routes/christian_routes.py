"""
Christian Corner Routes — SEMIRA FASHION
/protestant   — Protestant full suite
/catholic     — Catholic full suite
/api/christian/protestant-content  — JSON for home slider
/api/christian/catholic-content    — JSON for home slider
/api/christian/reading-plan        — JSON for a given day's Bible reading
"""

from flask import Blueprint, render_template, jsonify, request
from routes.shared import get_lang

christian_bp = Blueprint('christian', __name__)


@christian_bp.route('/protestant')
def protestant_suite():
    lang = get_lang()
    from database.christian_data import (
        PROTESTANT_BIBLE_VERSES, PROTESTANT_SONGS,
        get_today_protestant_verse, get_today_protestant_song,
    )
    return render_template(
        'customer/protestant.html',
        lang=lang,
        all_verses=PROTESTANT_BIBLE_VERSES,
        all_songs=PROTESTANT_SONGS,
        today_verse=get_today_protestant_verse(),
        today_song=get_today_protestant_song(),
    )


@christian_bp.route('/catholic')
def catholic_suite():
    lang = get_lang()
    from database.christian_data import (
        CATHOLIC_LITURGY, CATHOLIC_SAINT_PRAYERS,
        get_today_catholic_liturgy, get_today_catholic_prayer,
    )
    return render_template(
        'customer/catholic.html',
        lang=lang,
        all_liturgy=CATHOLIC_LITURGY,
        all_prayers=CATHOLIC_SAINT_PRAYERS,
        today_liturgy=get_today_catholic_liturgy(),
        today_prayer=get_today_catholic_prayer(),
    )


@christian_bp.route('/api/christian/protestant-content')
def api_protestant_content():
    from database.christian_data import get_today_protestant_verse, get_today_protestant_song
    return jsonify({
        'success': True,
        'verse': get_today_protestant_verse(),
        'song':  get_today_protestant_song(),
    })


@christian_bp.route('/api/christian/catholic-content')
def api_catholic_content():
    from database.christian_data import get_today_catholic_liturgy, get_today_catholic_prayer
    return jsonify({
        'success': True,
        'liturgy': get_today_catholic_liturgy(),
        'prayer':  get_today_catholic_prayer(),
    })


@christian_bp.route('/api/bible/books')
def api_bible_books():
    from database.bible_explorer import get_books_index
    result = get_books_index()
    return jsonify({'success': True, 'OT': result['OT'], 'NT': result['NT']})


@christian_bp.route('/api/bible/chapter')
def api_bible_chapter():
    from database.bible_explorer import get_chapter_verses
    code    = request.args.get('book', '').strip().upper()
    chapter = request.args.get('chapter', 1, type=int)
    if not code:
        return jsonify({'success': False, 'error': 'book is required'}), 400
    data = get_chapter_verses(code, chapter)
    if data is None:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return jsonify({'success': True, **data})


@christian_bp.route('/api/christian/reading-plan')
def api_reading_plan():
    from database.christian_data import get_reading_plan_day, get_today_reading_plan
    try:
        day_param = request.args.get('day')
        if day_param is not None:
            data = get_reading_plan_day(int(day_param))
        else:
            data = get_today_reading_plan()
        return jsonify({'success': True, 'plan': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
