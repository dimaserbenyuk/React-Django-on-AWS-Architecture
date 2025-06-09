FROM nginx:1.25.3-alpine

# Удаляем дефолтный конфиг
RUN rm /etc/nginx/conf.d/default.conf

# Копируем основной конфиг nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем виртуальный хост (app.conf)
COPY app.conf /etc/nginx/conf.d/app.conf

# Указываем рабочую директорию, если нужно (например, для static/media)
WORKDIR /usr/src/app

# Открываем порт
EXPOSE 80

# Запускаем nginx в форе
CMD ["nginx", "-g", "daemon off;"]
