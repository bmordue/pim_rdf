{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "rdf-pim-env";

  buildInputs = with pkgs; [
    # Apache Jena + Fuseki
    apache-jena
    apache-jena-fuseki

    # RDF syntax tools
    librdf_raptor2  # gives 'rapper'

    # Python RDF libraries
    (python3.withPackages (ps: with ps; [ rdflib ]))

    # unfree, can't run in CI as is
#    gemini-cli
#    claude-code
  ];

  shellHook = ''
    echo "RDF PIM Environment"
    echo "-------------------"
    echo "Available commands:"
    echo "  fuseki-server --config=config-pim.ttl"
    echo "  riot --validate file.ttl"
    echo "  rapper -i turtle file.ttl -o ntriples"
    echo ""
    echo "RDF base directory: pim_rdf_kb/"
  '';
}
