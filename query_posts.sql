SELECT 
    p.id as post_id,
    p.title as post_title,
    p."postType" as post_type,
    p."createdAt" as post_created_at,
    u.username,
    u.birthday as date_of_birth,
    pa.summary as post_summary,
    STRING_AGG(CONCAT('Category: ', pc.category::text, ', SubCategory: ', pc."subCategory"::text), '; ') as categories
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
    p."createdAt" DESC
LIMIT 100;