-- ==========================================
-- COMMUNITY PROGRAM EVALUATION
-- ==========================================


-- 1. Number of participants by program
SELECT
    pr.program_name,
    COUNT(p.participant_id) AS total_participants
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY total_participants DESC;


-- 2. Average outcome improvement by program
SELECT
    pr.program_name,
    ROUND(AVG(p.outcome_change), 2) AS average_outcome_change
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY average_outcome_change DESC;


-- 3. Program completion rate
SELECT
    pr.program_name,
    COUNT(p.participant_id) AS total_participants,
    SUM(
        CASE
            WHEN p.program_completed = 'Yes' THEN 1
            ELSE 0
        END
    ) AS completed_participants,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN p.program_completed = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(p.participant_id),
        2
    ) AS completion_rate
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY completion_rate DESC;


-- 4. Average satisfaction by program
SELECT
    pr.program_name,
    ROUND(
        AVG(p.satisfaction_score),
        2
    ) AS average_satisfaction
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY average_satisfaction DESC;


-- 5. Feedback category summary
SELECT
    feedback_category,
    COUNT(*) AS total_feedback
FROM participants
GROUP BY feedback_category
ORDER BY total_feedback DESC;