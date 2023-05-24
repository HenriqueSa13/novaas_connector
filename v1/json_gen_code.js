JG.repeat({
  assetAdministrationShells: [
    {
      hasDataSpecification: [],
      asset: {
        keys: [
          {
            type: "Asset",
            local: true,
            value: "https://example.asset.com/ids/asset/",
            index: 0,
            idType() {
              return JG.random("URI", "IRI");
            },
          },
        ],
      },
      identification: {
        id() {
          return "https://example.asset.com/ids/aas/" + JG.guid();
          //to get this id: _.trim(this.identification.id,'https://example.asset.com/ids/aas/')
        },
      },
      idShort() {
        return _.snakeCase(`${JG.firstName()} ${JG.lastName()}`) + "_asset";
      },
    },
  ],
  submodels: [
    {
      idShort: "OperationalData",
      submodelElements: [
        {
          //generate SubmodelElementColections or events
          idShort() {
            return _.snakeCase(JG.city());
          },
        },
      ],
    },
  ],
});
