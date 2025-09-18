FROM nginx:1.22.1-alpine

# FROM nginx:1.22.1

RUN mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx && \
    chmod -R 755 /var/cache/nginx
	
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY docs/ /usr/share/nginx/html/api/docs/