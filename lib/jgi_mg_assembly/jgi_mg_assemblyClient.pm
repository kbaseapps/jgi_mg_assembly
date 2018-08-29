package jgi_mg_assembly::jgi_mg_assemblyClient;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

jgi_mg_assembly::jgi_mg_assemblyClient

=head1 DESCRIPTION


A KBase module: jgi_mg_assembly


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => jgi_mg_assembly::jgi_mg_assemblyClient::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 run_mg_assembly_pipeline

  $results = $obj->run_mg_assembly_pipeline($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a jgi_mg_assembly.AssemblyPipelineParams
$results is a jgi_mg_assembly.AssemblyPipelineResults
AssemblyPipelineParams is a reference to a hash where the following keys are defined:
	reads_upa has a value which is a jgi_mg_assembly.reads_upa
	workspace_name has a value which is a string
	output_assembly_name has a value which is a string
	skip_rqcfilter has a value which is a jgi_mg_assembly.boolean
	debug has a value which is a jgi_mg_assembly.boolean
reads_upa is a string
boolean is an int
AssemblyPipelineResults is a reference to a hash where the following keys are defined:
	report_name has a value which is a string
	report_ref has a value which is a string
	assembly_output has a value which is a jgi_mg_assembly.assembly_upa
	cleaned_reads_output has a value which is a jgi_mg_assembly.reads_upa
	alignment_output has a value which is a jgi_mg_assembly.alignment_upa
assembly_upa is a string
alignment_upa is a string

</pre>

=end html

=begin text

$params is a jgi_mg_assembly.AssemblyPipelineParams
$results is a jgi_mg_assembly.AssemblyPipelineResults
AssemblyPipelineParams is a reference to a hash where the following keys are defined:
	reads_upa has a value which is a jgi_mg_assembly.reads_upa
	workspace_name has a value which is a string
	output_assembly_name has a value which is a string
	skip_rqcfilter has a value which is a jgi_mg_assembly.boolean
	debug has a value which is a jgi_mg_assembly.boolean
reads_upa is a string
boolean is an int
AssemblyPipelineResults is a reference to a hash where the following keys are defined:
	report_name has a value which is a string
	report_ref has a value which is a string
	assembly_output has a value which is a jgi_mg_assembly.assembly_upa
	cleaned_reads_output has a value which is a jgi_mg_assembly.reads_upa
	alignment_output has a value which is a jgi_mg_assembly.alignment_upa
assembly_upa is a string
alignment_upa is a string


=end text

=item Description



=back

=cut

 sub run_mg_assembly_pipeline
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function run_mg_assembly_pipeline (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to run_mg_assembly_pipeline:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'run_mg_assembly_pipeline');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "jgi_mg_assembly.run_mg_assembly_pipeline",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'run_mg_assembly_pipeline',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method run_mg_assembly_pipeline",
					    status_line => $self->{client}->status_line,
					    method_name => 'run_mg_assembly_pipeline',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "jgi_mg_assembly.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "jgi_mg_assembly.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'run_mg_assembly_pipeline',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method run_mg_assembly_pipeline",
            status_line => $self->{client}->status_line,
            method_name => 'run_mg_assembly_pipeline',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for jgi_mg_assembly::jgi_mg_assemblyClient\n";
    }
    if ($sMajor == 0) {
        warn "jgi_mg_assembly::jgi_mg_assemblyClient version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 boolean

=over 4



=item Description

A boolean - 0 for false, 1 for true.
    @range (0, 1)


=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 assembly_upa

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 reads_upa

=over 4



=item Description

Should be only Paired-end reads.


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 alignment_upa

=over 4



=item Description

Used for the alignment output.


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 AssemblyPipelineParams

=over 4



=item Description

Inputs for the Assembly pipeline.
reads_upa:
    UPA for the input reads object. This should be a Paired-End Illumina reads file.
workspace_name:
    name of the workspace to upload to at the end.
output_assembly_name:
    name of the output assembly file.
skip_rqcfilter:
    If 1, skip the RQCFilter step of the pipeline. If 0, run it. (default = 0)
cleaned_reads_name (optional):
    If not empty, this will cause the finalized, cleaned/filtered reads to be uploaded as a new
    reads object with this name. This'll be an interleaved paired-end reads object.
alignment_name (optional):
    If not empty, this will save and upload the BBMap-generated BAM file that aligns the original
    filtered, but uncleaned reads to the constructed assembly.
debug (hidden option):
    If 1, run in debug mode. A little more verbose, and trims some parameters from various steps
    so it can run locally(ish). You probably don't want to do this in production, it's meant for
    testing.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
reads_upa has a value which is a jgi_mg_assembly.reads_upa
workspace_name has a value which is a string
output_assembly_name has a value which is a string
skip_rqcfilter has a value which is a jgi_mg_assembly.boolean
debug has a value which is a jgi_mg_assembly.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
reads_upa has a value which is a jgi_mg_assembly.reads_upa
workspace_name has a value which is a string
output_assembly_name has a value which is a string
skip_rqcfilter has a value which is a jgi_mg_assembly.boolean
debug has a value which is a jgi_mg_assembly.boolean


=end text

=back



=head2 AssemblyPipelineResults

=over 4



=item Description

Outputs from the Assembly pipeline.
report_name:
    The name of the generated report object.
report_ref:
    The UPA for the generated report object.
assembly_output:
    The UPA for the newly made assembly object.
cleaned_reads_output (optional):
    The UPA for the finalized, cleaned reads that are assembled in the pipeline, if requested by the input.
alignment_output (optional):
    The UPA for the uploaded alignment object, if requested by the input.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a string
report_ref has a value which is a string
assembly_output has a value which is a jgi_mg_assembly.assembly_upa
cleaned_reads_output has a value which is a jgi_mg_assembly.reads_upa
alignment_output has a value which is a jgi_mg_assembly.alignment_upa

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a string
report_ref has a value which is a string
assembly_output has a value which is a jgi_mg_assembly.assembly_upa
cleaned_reads_output has a value which is a jgi_mg_assembly.reads_upa
alignment_output has a value which is a jgi_mg_assembly.alignment_upa


=end text

=back



=cut

package jgi_mg_assembly::jgi_mg_assemblyClient::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
