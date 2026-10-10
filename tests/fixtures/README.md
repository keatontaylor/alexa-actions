`localhost-cert.pem` and `localhost-key.pem` are public, disposable loopback test
fixtures. They are not deployment credentials and must never be used by a real
service. The self-signed certificate expires in October 2036. Tests use it to
verify that the default TLS configuration rejects an untrusted certificate and
that the explicit `VERIFY_SSL=false` setting permits it with a warning.

To regenerate:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -keyout tests/fixtures/localhost-key.pem -out tests/fixtures/localhost-cert.pem -days 3650 -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1'
```
