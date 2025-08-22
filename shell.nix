{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "rdf-pim-env";

  buildInputs = [
    # Apache Jena + Fuseki
    pkgs.apache-jena
    pkgs.apache-jena-fuseki

    # RDF syntax tools
    pkgs.librdf_raptor2  # gives 'rapper'

    # Python RDF libraries
    (pkgs.python3.withPackages (ps: with ps; [ rdflib pyshacl ]))
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
