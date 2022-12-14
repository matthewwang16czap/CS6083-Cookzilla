create view recipe_avgstars as
select r.recipeID, r.title, r.numServings, r.postedBy, IFNULL(a.avgstars, 0) as avgstars
from recipe r left join (
	select recipeID, avg(stars) as avgstars
    from review
	group by recipeID
) a on r.recipeID = a.recipeID
;