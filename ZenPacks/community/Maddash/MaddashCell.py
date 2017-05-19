from . import schema

class MaddashCell(schema.MaddashCell):
    """Class override to get rrd template based on check type"""

    # see example in zenpacklib yaml reference 'Extending ZenPackLib Classes'
    def getRRDTemplates(self):
        for template in super(MaddashCell, self).getRRDTemplates():
            if self.check_type == 'throughput' and template.id == 'throughput':
                return [ template ]
            if self.check_type == 'packet loss' and template.id == 'packet_loss':
                return [ template ]
            if self.check_type == 'latency' and template.id == 'latency':
                return [ template ]
