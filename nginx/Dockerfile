FROM nginx:1.25.3-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf

COPY app.conf /etc/nginx/conf.d/app.conf

WORKDIR /usr/src/app

EXPOSE 80


CMD ["nginx", "-g", "daemon off;"]
