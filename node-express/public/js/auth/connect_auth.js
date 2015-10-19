/**
 * Konfigurer JSO modul for bruk med denne klienten og start autentiseringsflyt. 
 *
 * Med referanser til DASHBOARD menes https://dashboard.feideconnect.no.
 * 
 * 1. Gi denne fila navnet connect_auth.js (fjern '-SAMPLE')
 * 2. Registrer en ny klient i DASHBOARD
 * 3. Fyll inn linjene 19-21 med info fra DASHBOARD
 * 
 * @author Simon Skrødal
 * @since August 2015
 */
 
 var CONNECT_AUTH = (function () {
	 
	 var CONFIG = 
	 {
		 fc_auth : {
			providerID		: 	"HVA SOM HELST",	// Valgfritt
			client_id		:	"MÅ FYLLES INN",	// Klient-spesifikk, satt i DASHBOARD
			redirect_uri	: 	"MÅ FYLLES INN",	// Klient-spesifikk, settes i DASHBOARD
			authorization	: 	"https://auth.feideconnect.no/oauth/authorization"		// Alltid samme
		 },
		 fc_endpoints :	{
			// For tilgang må klienten ha bedt om dette scopet i Dashboard
			groups: 	"https://groups-api.feideconnect.no/groups/groups",
			// Base-URL for bildefil 		
			photo: 		"https://auth.feideconnect.no/user/media/",					
			// BrukerID, navn og profilbilde. For mer info (eks. epost, Feide-ting) må scopes etterspørres i Dashboard.
			userinfo: 	"https://auth.feideconnect.no/userinfo"
			// People api (cross origin issues: pilot version is not ready for use)
			people: 	"https://auth.feideconnect.no/peoplesearch/search/uit.no/
		 }, 
		 api_endpoints : {
			// Andre 3.parts-APIer klienten har tilgang til via Connect (DASHBOARD) 
			simons_vitser : 'https://simons-vitser.gk.feideconnect.no/api/connect-simons-vitser/'
			feide_chat: 'http://localhost:3001/'
		 }, 
		 links : {
			 client_source	: 'https://github.com/skrodal/connect-simple-demo',
			 api_source 	: 'https://github.com/skrodal/connect-simons-vitser/'
		 }
	 };

	// 
	return {
		// Dreper sesjonen, inkludert Feide-sesj.
		logout: function(){
			window.location.replace("https://auth.feideconnect.no/logout");
		},
		config : function (){
			return CONFIG;
		}
	};

})();
