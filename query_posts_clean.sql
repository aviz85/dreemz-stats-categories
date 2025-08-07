SELECT 
    p.id as post_id,
    p.title as post_title,
    p."postType" as post_type,
    TO_CHAR(p."createdAt", 'YYYY-MM-DD HH24:MI:SS') as post_created_at,
    COALESCE(u.username, 'N/A') as username,
    CASE 
        WHEN u.birthday IS NOT NULL THEN TO_CHAR(u.birthday, 'YYYY-MM-DD')
        ELSE 'N/A'
    END as date_of_birth,
    COALESCE(pa.summary, 'No summary available') as post_summary,
    COALESCE(
        STRING_AGG(
            CONCAT('Category: ', pc.category::text, ', SubCategory: ', pc."subCategory"::text), 
            '; '
        ),
        'No categories'
    ) as categories
FROM 
    postdetails p
LEFT JOIN 
    userdetails u ON p."ownerId" = u.id::text
LEFT JOIN 
    post_analyze pa ON p.id = pa."postId"
LEFT JOIN 
    post_category pc ON p.id = pc."postId"
WHERE 
    p."postType" IN (0, 1)
    AND p."isDeleted" = false
GROUP BY 
    p.id, p.title, p."postType", p."createdAt", 
    u.username, u.birthday, pa.summary
ORDER BY 
    p."createdAt" DESC;