grammar ArmPseudo;

program: statement+ EOF;

statement
    : assignment ';'
    | constantDecl ';'
    | typedAssignment ';'
    | tupleAssignment ';'
    | functionCall ';'
    | loopStmt
    | ifStmt
    | caseStmt
    ;

constantDecl
    : 'constant' type IDENTIFIER '=' expression
    ;

typedAssignment
    : IDENTIFIER IDENTIFIER '=' expression
    ;

assignment
    : type IDENTIFIER ('=' expression)?
    | lvalue '=' expression
    ;

lvalue
    : IDENTIFIER slice?
    | IDENTIFIER '[' indexList ']'
    | IDENTIFIER '[' ']'
    ;

tupleAssignment
    : '<' tupleElements '>' '=' expression
    ;

tupleElements
    : IDENTIFIER (',' IDENTIFIER)*
    ;

loopStmt
    : 'for' IDENTIFIER '=' expression 'to' expression block
    ;

ifStmt
    : 'if' expression 'then' block ('else' ifStmt | 'else' block)?
    ;

caseStmt
    : 'case' expression 'of' '{' whenClause+ '}'
    ;

whenClause
    : 'when' expression block
    ;

condition
    : expression
    ;

block
    : '{' statement* '}'
    ;

functionCall
    : scopedIdentifier '(' argumentList? ')'
    ;

expression
    : expression op=('EOR' | 'AND' | 'OR' | 'DIV' | 'MOD' | '*' | '/' | '+' | '-' | '<<' | '>>' | '&' | '|' | ':' | '==' | '!=') expression # BinaryExpr
    | 'if' expression 'then' expression 'else' expression                                                  # TernaryExpr
    | functionCall                                                                                          # FuncExpr
    | IDENTIFIER slice                                                                                      # SliceExpr
    | IDENTIFIER '[' indexList ']'                                                                          # IndexExpr
    | IDENTIFIER '[' ']'                                                                                    # EmptyIndexExpr
    | IDENTIFIER                                                                                            # IdentifierExpr
    | '(' expression ')'                                                                                    # ParenExpr
    | INTEGER                                                                                               # IntExpr
    ;

slice
    : '<' expression ':' expression '>'
    ;

indexList
    : expression (',' expression)*
    ;

argumentList
    : expression (',' expression)*
    ;

type
    : 'bits' '(' expression ')'
    | 'integer'
    ;

scopedIdentifier
    : IDENTIFIER ('.' IDENTIFIER)*
    ;

IDENTIFIER: [a-zA-Z_] [a-zA-Z_0-9]*;
INTEGER: [0-9]+;
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;

