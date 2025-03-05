# https://github.com/TechEmpower/FrameworkBenchmarks/blob/67dd5899a0f34feaecd96bef5357ab4ea219c4c8/frameworks/PHP/laravel/laravel.dockerfile
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -yqq && apt-get install -yqq software-properties-common > /dev/null
RUN LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php > /dev/null && \
    apt-get update -yqq > /dev/null && apt-get upgrade -yqq > /dev/null

RUN apt-get install -yqq nginx git unzip \
    php8.4-cli php8.4-fpm php8.4-pgsql  php8.4-mbstring php8.4-xml  php8.4-curl > /dev/null

COPY --from=composer --link /usr/bin/composer /usr/local/bin/composer

COPY --link deploy/conf/* /etc/php/8.4/fpm/
WORKDIR /laravel
COPY --link . .

RUN mkdir -p bootstrap/cache \
            storage/logs \
            storage/framework/sessions \
            storage/framework/views \
            storage/framework/cache

# replace DB_HOST=postgresql in .env with DB_HOST=VALUE_FROM_ARG
ARG POSTGRES_HOST
RUN sed -i "s/DB_HOST=postgresql/DB_HOST=$POSTGRES_HOST/g" .env

RUN composer install --optimize-autoloader --classmap-authoritative --no-dev --quiet
RUN php artisan optimize
RUN chown -R www-data:www-data /laravel

EXPOSE 8080

# Uncomment next line for Laravel console error logging to be viewable in docker logs
# RUN echo "catch_workers_output = yes" >> /etc/php/8.4/fpm/php-fpm.conf

CMD service php8.4-fpm start && \
    nginx -c /laravel/deploy/nginx.conf
