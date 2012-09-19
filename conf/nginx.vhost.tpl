server {
    #listen   80; ## listen for ipv4; this line is default and implied
    #listen   [::]:80 default ipv6only=on; ## listen for ipv6
#   listen 443;
#
#   ssl on;
#   ssl_certificate cert.pem;
#   ssl_certificate_key cert.key;
#
#   ssl_session_timeout 5m;
#
#   ssl_protocols SSLv3 TLSv1;
#   ssl_ciphers ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv3:+EXP;
#   ssl_prefer_server_ciphers on;
#
#
    root {{ staticroot }};
    index index.html index.htm;

    # Make site accessible from http://fqdn/
    server_name {{ fqdn }};

    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to index.html
        #try_files $uri $uri/ /index.html;
        uwsgi_pass   127.0.0.1:{{ uwsgi_port }};
        include      uwsgi_params;
        # Uncomment to enable naxsi on this location
        # include /etc/nginx/naxsi.rules
    }

} # end PDS block
