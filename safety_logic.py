def evaluate_safety_state(ladle_cover_missing, degassing_advanced_early, geofence_breach, casting_sequence_active):
    """
    Evaluates the safety state across the three pillars.
    Returns:
        interlock_locked (bool): True if any critical failure occurred.
        safety_score (str): '100% — OPTIMAL' or 'CRITICAL — SECURE COMPLIANCE'
        alerts (list): List of active alert messages.
    """
    alerts = []
    interlock_locked = False

    # Pillar 1: Structural Non-Compliance
    if ladle_cover_missing:
        alerts.append("STRUCTURAL ANOMALY: Ladle Safety Cover Missing!")
        interlock_locked = True

    # Pillar 2: Process-Skipping Watchdog
    if degassing_advanced_early:
        alerts.append("PROTOCOL VIOLATION: Degassing advanced before completion!")
        interlock_locked = True

    # Pillar 3: Proximity Protection
    if geofence_breach and casting_sequence_active:
        alerts.append("CRITICAL ALERT: BLAST ZONE BREACHED!")
        interlock_locked = True

    safety_score = "100% — OPTIMAL" if not interlock_locked else "CRITICAL — SECURE COMPLIANCE"

    return interlock_locked, safety_score, alerts
