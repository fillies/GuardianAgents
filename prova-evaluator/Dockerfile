FROM omnifish/glassfish

# Copy the WAR file into the container
COPY target/prova-evaluator-1.0-SNAPSHOT.war /opt/glassfish7/glassfish/domains/domain1/autodeploy/

# Expose the port
EXPOSE 8080

# Run the GlassFish server
CMD ["asadmin", "start-domain", "--verbose", "domain1"]
