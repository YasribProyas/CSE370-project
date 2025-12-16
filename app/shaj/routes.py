from flask import render_template
from app.shaj import shaj_bp
from app.db import execute_query

@shaj_bp.route('/donation')
def donation():
    result = execute_query("SELECT SUM(amount) as total FROM Donation", fetch=True)
    total_donations = result[0]['total'] if result and result[0]['total'] else 0
    
    count_result = execute_query("SELECT COUNT(*) as count FROM Donation", fetch=True)
    donation_count = count_result[0]['count'] if count_result else 0
    
    recent_query = """
        SELECT d.*, u.name as donor_name 
        FROM Donation d 
        LEFT JOIN User u ON d.user_id = u.id 
        ORDER BY d.id DESC 
        LIMIT 10
    """
    recent_donations = execute_query(recent_query, fetch=True) or []
    
    return render_template('donation.html', 
                         total_donations=total_donations,
                         donation_count=donation_count,
                         recent_donations=recent_donations)