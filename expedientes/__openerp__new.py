{
    "name" : "escribanodocumentos",
    "version" : "1.0",
    "author" : "Datamatic",
    "website" : "www.datamatic.com.uy",
    "category" : "escribanodocumentos",
    "description": """ Gestion de Ficheros """,
    "depends" : ['base','crm_claim','project'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['escribanodocumentos_view.xml',
                    'partner_view.xml',
                    'conceptosdocumentos_view.xml',
                    'historialdoc_view.xml',
		    'report/report_print_report.xml'
	],                    
    "installable": True,
    "active": False,
}
