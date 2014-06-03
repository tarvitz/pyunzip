# coding: utf-8
#(application,model)
CORE_SEARCH_MAP=('title','content','comments','comment')
#mapping:
#first field - application
#second field - model
#third - models fields
#fourth - extra options for searching (for example do not search comments which was hidden: is_removed=False)
CORE_SEARCH_FIELDS=(
    ('news','news',
        ('title','author','editor','url','head_content','content','date',),
        {
            'approved': True,
        }
    ),
    ('files','replay',
        ('name','version__name','upload_date','type','nonstd_layout','teams','races','winner','author__nickname','comments'),
        {},
    ),
    ('files','image',
        ('title','comments','owner__nickname'),
        {}
    ),
    ('comments','comment',
        (),
        {
            'is_removed':False,
            'is_public':True,
        }
    ),
    ('quotes','quote',
        ('date_add','date_pub','text','author__nickname','moderator__nickname','tags'),
        {},
    ),
    ('news','archivednews',
        ('title','author','editor','url','head_content','content','date',),
        {}
    ),
    ('tabletop','roster',
        ('title','user__nickname','player','comments','custom_race'),
        {}
    ),
    ('tabletop','battlereport',
        ('winner__user__nickname','comment',),
        {'approved': True}
    ),
    #('auth','user',
    #    ('nickname',),
    #    {},
    #),
)

