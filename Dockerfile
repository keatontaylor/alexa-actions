FROM python:3.12 as builder

WORKDIR /app
COPY ./lambda/config.py .
COPY ./lambda/const.py .
COPY ./lambda/schemas.py .
COPY ./lambda/language_strings.json .
COPY ./lambda/prompts.py .
COPY ./lambda/requirements.txt .
COPY ./lambda/lambda_function.py .

RUN pip install -t . -r requirements.txt

FROM alpine:latest as tailscale
WORKDIR /app
COPY . ./
ENV TSFILE=tailscale_1.64.0_amd64.tgz
RUN wget https://pkgs.tailscale.com/stable/${TSFILE} && \
  tar xzf ${TSFILE} --strip-components=1
COPY . ./


FROM public.ecr.aws/lambda/python:3.12
#can't test locally without it
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/local/bin/aws-lambda-rie
RUN chmod 755 /usr/local/bin/aws-lambda-rie

COPY ./custom_entrypoint /var/runtime/custom_entrypoint
COPY --from=builder /app/ /var/task
COPY --from=tailscale /app/tailscaled /var/runtime/tailscaled
COPY --from=tailscale /app/tailscale /var/runtime/tailscale
RUN mkdir -p /var/run && ln -s /tmp/tailscale /var/run/tailscale && \
  mkdir -p /var/cache && ln -s /tmp/tailscale /var/cache/tailscale && \
  mkdir -p /var/lib && ln -s /tmp/tailscale /var/lib/tailscale && \
  mkdir -p /var/task && ln -s /tmp/tailscale /var/task/tailscale

# Run on container startup.
EXPOSE 8080
ENTRYPOINT ["/var/runtime/custom_entrypoint"]
CMD [ "lambda_function.lambda_handler" ]
